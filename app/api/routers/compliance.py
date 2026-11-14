from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import Role
from app.models.compliance import EmasSyncLog, GovernmentReport
from app.models.user import User
from app.services.export_service import (
    isb_report,
    military_report_csv,
    unified_declaration_csv,
    unified_declaration_rows,
)

router = APIRouter(tags=["M04 · Dövlət Portalları və Uyğunluq"])

PAYROLL = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.ACCOUNTANT}
COMPLIANCE_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.ACCOUNTANT, Role.HR_SPECIALIST}


def _check_org(user: User, organization_id: int | None) -> None:
    if (
        user.role != Role.SUPERADMIN.value
        and user.organization_id is not None
        and organization_id != user.organization_id
    ):
        raise HTTPException(status_code=404, detail="Təşkilat tapılmadı")


@router.get("/compliance/unified-declaration")
def unified_declaration(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    organization_id: int | None = Query(None),
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL)),
):
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    _check_org(user, org_id)
    if format == "csv":
        content = unified_declaration_csv(db, org_id, year, month)
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="vahid-beyanname-{year}-{month:02d}.csv"'
            },
        )
    return unified_declaration_rows(db, org_id, year, month)


@router.get("/compliance/isb-report")
def isb(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PAYROLL)),
):
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    _check_org(user, org_id)
    try:
        return isb_report(db, org_id, year, month)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/compliance/military-report")
def military_report(
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*COMPLIANCE_WRITE)),
):
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    _check_org(user, org_id)
    content = military_report_csv(db, org_id)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="herbi-ucot-forma-t2-{org_id}.csv"'
        },
    )


@router.post("/compliance/emas/queue", status_code=201)
def queue_emas(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*COMPLIANCE_WRITE)),
):
    org_id = payload.get("organization_id") or user.organization_id
    _check_org(user, org_id)
    log = EmasSyncLog(
        organization_id=org_id,
        entity_type=payload.get("entity_type", "EMPLOYEE"),
        entity_id=payload.get("entity_id", 0),
        action_type=payload.get("action_type", "SYNC"),
        request_payload=payload.get("request_payload", {}),
        response_payload={},
        emas_status="QUEUED",
        retry_count=0,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return serialize(log)


@router.post("/compliance/emas/{log_id}/mark-synced")
def mark_emas_synced(
    log_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*COMPLIANCE_WRITE)),
):
    log = db.get(EmasSyncLog, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log tapılmadı")
    _check_org(user, log.organization_id)
    log.emas_status = payload.get("emas_status", "SYNCED")
    log.response_payload = payload.get("response_payload", {})
    log.synced_at = datetime.now(timezone.utc)
    db.commit()
    return serialize(log)


router.include_router(
    build_crud_router(
        model=EmasSyncLog,
        prefix="/emas-sync-logs",
        tags=["M04 · ƏMAS Sinxronizasiya"],
        allowed_fields={
            "organization_id", "entity_type", "entity_id", "action_type",
            "request_payload", "response_payload", "emas_status", "retry_count", "synced_at",
        },
        read_roles=COMPLIANCE_WRITE,
        write_roles=COMPLIANCE_WRITE,
        order_by="id",
    )
)
router.include_router(
    build_crud_router(
        model=GovernmentReport,
        prefix="/government-reports",
        tags=["M04 · Dövlət Hesabatları"],
        allowed_fields={
            "organization_id", "report_type", "period_year", "period_month",
            "period_quarter", "headcount", "fund_total", "payload_json", "status",
        },
        read_roles=COMPLIANCE_WRITE,
        write_roles=COMPLIANCE_WRITE,
        order_by="id",
    )
)
