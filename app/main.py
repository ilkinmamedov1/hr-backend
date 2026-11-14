import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import DataError, IntegrityError, StatementError
from sqlalchemy.orm import Session

from app.api.routers import (
    analytics,
    auth,
    compliance,
    contracts,
    employees,
    ess,
    leave,
    meta,
    organizations,
    payroll,
    performance,
    recruitment,
    safety,
    time,
    training,
    trips,
    workflow,
)
from app.core.audit import current_ip, current_user_id
from app.core.config import settings
from app.core.database import SessionLocal, get_db, init_db
from app.core.security import decode_token
from app.seed import seed_all

logger = logging.getLogger("hr_erp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.AUTO_SEED:
        with SessionLocal() as db:
            seed_all(db)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Azərbaycan Əmək Məcəlləsi, Vergi Məcəlləsi, DSMF, İTS və ƏMAS uyğun "
        "HR & Payroll ERP sistemi. Bütün modullar: M01-M14."
    ),
    lifespan=lifespan,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

if settings.allowed_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def audit_context_middleware(request: Request, call_next):
    current_user_id.set(None)
    current_ip.set(request.client.host if request.client else None)
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        try:
            payload = decode_token(authorization.split(" ", 1)[1])
            current_user_id.set(int(payload.get("sub")))
        except Exception:
            pass
    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > settings.MAX_REQUEST_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Sorğu ölçüsü həddi aşır"})
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'",
        )
    return response


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("IntegrityError on %s: %s", request.url.path, exc.orig)
    return JSONResponse(
        status_code=409,
        content={"detail": "Məlumat bazası məhdudiyyəti pozuldu"},
    )


@app.exception_handler(DataError)
async def data_error_handler(request: Request, exc: DataError):
    logger.warning("DataError on %s: %s", request.url.path, exc.orig)
    return JSONResponse(
        status_code=400,
        content={"detail": "Yanlış məlumat formatı"},
    )


@app.exception_handler(StatementError)
async def statement_error_handler(request: Request, exc: StatementError):
    logger.warning("StatementError on %s: %s", request.url.path, exc.orig)
    return JSONResponse(
        status_code=400,
        content={"detail": "Sorğu emal edilə bilmədi"},
    )


@app.get("/api", tags=["System"])
def api_info():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.ENABLE_DOCS else None,
        "api": settings.API_V1_PREFIX,
        "demo_enabled": settings.SEED_DEMO,
        "modules": [f"M{i:02d}" for i in range(1, 15)],
    }


@app.get(f"{settings.API_V1_PREFIX}/system/info", tags=["System"])
def system_info():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "demo_enabled": settings.SEED_DEMO,
        "docs_enabled": settings.ENABLE_DOCS,
        "api": settings.API_V1_PREFIX,
    }


@app.get("/health", tags=["System"])
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        raise HTTPException(status_code=503, detail="Verilənlər bazası əlçatan deyil")
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(
        STATIC_DIR / "index.html",
        headers={"Cache-Control": "no-store"},
    )


for router in (
    auth.router,
    organizations.router,
    employees.router,
    contracts.router,
    compliance.router,
    time.router,
    leave.router,
    payroll.router,
    trips.router,
    recruitment.router,
    performance.router,
    training.router,
    safety.router,
    analytics.router,
    workflow.router,
    ess.router,
    meta.router,
):
    app.include_router(router, prefix=settings.API_V1_PREFIX)
