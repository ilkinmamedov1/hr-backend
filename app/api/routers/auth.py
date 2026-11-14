from collections import defaultdict, deque
from datetime import datetime, timezone
from threading import Lock
from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.config import settings
from app.core.database import get_db
from app.core.rbac import Role
from app.core.security import create_access_token, hash_password, verify_password
from app.models.employee import Employee
from app.models.user import User
from app.schemas.auth import (
    ChangePassword,
    PasswordReset,
    Token,
    UserCreate,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["M14 · Auth & İstifadəçilər"])

PRIVILEGED_ROLES = {Role.SUPERADMIN.value, Role.HR_DIRECTOR.value}
_login_attempts: dict[str, deque] = defaultdict(deque)
_login_lock = Lock()


def _login_keys(request: Request, email: str) -> tuple[str, str]:
    ip = request.client.host if request.client else "unknown"
    return f"ip:{ip}", f"id:{ip}:{email}"


def _check_login_rate(request: Request, email: str) -> tuple[str, str]:
    keys = _login_keys(request, email)
    now = monotonic()
    window = settings.LOGIN_WINDOW_MINUTES * 60
    with _login_lock:
        for key in keys:
            attempts = _login_attempts[key]
            while attempts and now - attempts[0] > window:
                attempts.popleft()
            if len(attempts) >= settings.LOGIN_MAX_ATTEMPTS:
                raise HTTPException(
                    status_code=429,
                    detail="Çox sayda uğursuz giriş cəhdi. Bir az sonra yenidən yoxlayın.",
                    headers={"Retry-After": str(window)},
                )
    return keys


def _record_login_failure(keys: tuple[str, str]) -> None:
    now = monotonic()
    with _login_lock:
        for key in keys:
            _login_attempts[key].append(now)


def _clear_login_failures(keys: tuple[str, str]) -> None:
    with _login_lock:
        for key in keys:
            _login_attempts.pop(key, None)


def _validate_employee_link(
    employee_id: int | None, organization_id: int | None, db: Session
) -> None:
    if employee_id is None:
        return
    employee = db.get(Employee, employee_id)
    if employee is None or (
        organization_id is not None and employee.organization_id != organization_id
    ):
        raise HTTPException(status_code=400, detail="İşçi tapılmadı")


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form_data.username.lower()
    rate_keys = _check_login_rate(request, email)
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(form_data.password, user.hashed_password):
        _record_login_failure(rate_keys)
        raise HTTPException(status_code=401, detail="Email və ya şifrə yanlışdır")
    if not user.is_active:
        _record_login_failure(rate_keys)
        raise HTTPException(status_code=403, detail="İstifadəçi deaktivdir")

    _clear_login_failures(rate_keys)
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    token = create_access_token(
        str(user.id),
        user.role,
        {
            "org": user.organization_id,
            "name": user.full_name,
            "tv": int(user.token_version or 0),
        },
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "user": user,
    }


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/change-password")
def change_password(
    payload: ChangePassword,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Köhnə şifrə yanlışdır")
    user.hashed_password = hash_password(payload.new_password)
    user.token_version = int(user.token_version or 0) + 1
    db.commit()
    return {"detail": "Şifrə dəyişdirildi"}


@router.get("/roles")
def list_roles(user: User = Depends(get_current_user)):
    return [role.value for role in Role]


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.SUPERADMIN, Role.HR_DIRECTOR)),
):
    stmt = select(User).order_by(User.id)
    if user.role != Role.SUPERADMIN.value and user.organization_id:
        stmt = stmt.where(User.organization_id == user.organization_id)
    return [UserRead.model_validate(row) for row in db.scalars(stmt)]


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.SUPERADMIN, Role.HR_DIRECTOR)),
):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Bu email artıq qeydiyyatdadır")
    if payload.role not in {role.value for role in Role}:
        raise HTTPException(status_code=400, detail="Yanlış rol")
    if user.role != Role.SUPERADMIN.value and payload.role in PRIVILEGED_ROLES:
        raise HTTPException(status_code=403, detail="Bu rolu təyin etmək icazəniz yoxdur")

    org_id = payload.organization_id
    if user.role != Role.SUPERADMIN.value:
        org_id = user.organization_id
    _validate_employee_link(payload.employee_id, org_id, db)

    new_user = User(
        email=email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        organization_id=org_id,
        employee_id=payload.employee_id,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.SUPERADMIN, Role.HR_DIRECTOR)),
):
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="İstifadəçi tapılmadı")
    data = payload.model_dump(exclude_unset=True)
    if user.role != Role.SUPERADMIN.value:
        if (
            target.organization_id != user.organization_id
            or target.role in PRIVILEGED_ROLES
            or data.get("role") in PRIVILEGED_ROLES
        ):
            raise HTTPException(status_code=404, detail="İstifadəçi tapılmadı")
        data.pop("organization_id", None)
    if target.id == user.id:
        if data.get("is_active") is False:
            raise HTTPException(status_code=400, detail="Öz hesabınızı deaktiv edə bilməzsiniz")
        if "role" in data and data["role"] != target.role:
            raise HTTPException(status_code=400, detail="Öz rolunuzu dəyişə bilməzsiniz")
    if "role" in data and data["role"] not in {role.value for role in Role}:
        raise HTTPException(status_code=400, detail="Yanlış rol")
    _validate_employee_link(
        data.get("employee_id", target.employee_id),
        data.get("organization_id", target.organization_id),
        db,
    )
    sensitive = {"role", "organization_id", "employee_id", "is_active"}
    for key, value in data.items():
        setattr(target, key, value)
    if sensitive.intersection(data):
        target.token_version = int(target.token_version or 0) + 1
    db.commit()
    db.refresh(target)
    return target


@router.post("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    payload: PasswordReset,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.SUPERADMIN, Role.HR_DIRECTOR)),
):
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="İstifadəçi tapılmadı")
    if user.role != Role.SUPERADMIN.value and (
        target.organization_id != user.organization_id
        or target.role in PRIVILEGED_ROLES
    ):
        raise HTTPException(status_code=404, detail="İstifadəçi tapılmadı")
    target.hashed_password = hash_password(payload.new_password)
    target.token_version = int(target.token_version or 0) + 1
    db.commit()
    return {"detail": "Şifrə yeniləndi"}
