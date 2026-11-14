from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Any, Callable

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Numeric, Time, asc, desc, func, inspect, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.rbac import ALL_ROLES, Role
from app.models.employee import Employee
from app.models.organization import Organization
from app.models.user import User

RESERVED_QUERY = {"skip", "limit", "q", "sort", "include_deleted", "format"}

ENTITY_ACL: dict[str, dict[str, list[str]]] = {}


def _role_names(roles) -> list[str]:
    names = {str(role) for role in roles}
    names.add(Role.SUPERADMIN.value)
    return sorted(names)


def register_entity_acl(
    prefix: str, read_roles, write_roles, delete_roles
) -> None:
    ENTITY_ACL[prefix.strip("/")] = {
        "read_roles": _role_names(read_roles),
        "write_roles": _role_names(write_roles),
        "delete_roles": _role_names(delete_roles),
    }


def to_json(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, list):
        return [to_json(v) for v in value]
    if isinstance(value, dict):
        return {k: to_json(v) for k, v in value.items()}
    return str(value)


def serialize(obj, exclude: set[str] | None = None) -> dict:
    exclude = exclude or set()
    data = {}
    for attr in inspect(obj).mapper.column_attrs:
        if attr.key in exclude:
            continue
        data[attr.key] = to_json(getattr(obj, attr.key, None))
    return data


def has_column(model, name: str) -> bool:
    return name in model.__table__.columns


def _parse_datetime(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def coerce_payload(model, data: dict) -> dict:
    columns = {col.key: col for col in model.__table__.columns}
    for key, value in list(data.items()):
        col = columns.get(key)
        if col is None or value is None:
            continue
        if value == "":
            data[key] = None
            continue
        try:
            if isinstance(col.type, DateTime) and isinstance(value, str):
                data[key] = _parse_datetime(value)
            elif isinstance(col.type, Date) and isinstance(value, str):
                data[key] = date.fromisoformat(value.strip())
            elif isinstance(col.type, Time) and isinstance(value, str):
                data[key] = time.fromisoformat(value.strip())
            elif isinstance(col.type, Numeric) and isinstance(value, str):
                data[key] = Decimal(value)
            elif isinstance(col.type, Boolean) and isinstance(value, str):
                data[key] = value.strip().lower() in ("1", "true", "yes", "bəli", "beli")
            elif isinstance(col.type, (Integer, Float)) and isinstance(value, str):
                data[key] = float(value) if isinstance(col.type, Float) else int(value)
        except (ValueError, ArithmeticError) as exc:
            raise HTTPException(status_code=400, detail=f"{key} dəyəri düzgün deyil: {exc}")
    return data


def ensure_org_access(model, obj, user: User, db: Session | None = None) -> None:
    if user.role == Role.SUPERADMIN.value or user.organization_id is None:
        return
    if model is Organization:
        if obj.id != user.organization_id:
            raise HTTPException(status_code=404, detail="Qeyd tapılmadı")
        return
    if has_column(model, "organization_id"):
        if getattr(obj, "organization_id", None) != user.organization_id:
            raise HTTPException(status_code=404, detail="Qeyd tapılmadı")
    elif has_column(model, "employee_id") and db is not None:
        employee = db.get(Employee, getattr(obj, "employee_id", None))
        if employee is None or employee.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Qeyd tapılmadı")


def _validate_org_employee(model, data: dict, user: User, db: Session) -> None:
    if user.role == Role.SUPERADMIN.value or user.organization_id is None:
        return
    if has_column(model, "organization_id") or not has_column(model, "employee_id"):
        return
    if "employee_id" not in data:
        return
    employee = db.get(Employee, data.get("employee_id"))
    if employee is None or employee.organization_id != user.organization_id:
        raise HTTPException(status_code=400, detail="İşçi tapılmadı")


def _validate_org_relation(
    relation_model, relation_field: str | None, data: dict, user: User, db: Session
) -> None:
    if (
        relation_model is None
        or relation_field is None
        or user.role == Role.SUPERADMIN.value
        or user.organization_id is None
        or relation_field not in data
    ):
        return
    related = db.get(relation_model, data.get(relation_field))
    if related is None or related.organization_id != user.organization_id:
        raise HTTPException(status_code=400, detail="Əlaqəli qeyd tapılmadı")


def build_crud_router(
    *,
    model,
    prefix: str,
    tags: list[str],
    allowed_fields: set[str],
    read_roles: set = ALL_ROLES,
    write_roles: set = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST},
    delete_roles: set | None = None,
    search_fields: tuple[str, ...] = (),
    order_by: str = "id",
    exclude_fields: set[str] | None = None,
    before_create: Callable | None = None,
    after_create: Callable | None = None,
    before_update: Callable | None = None,
    soft_delete: bool = False,
    org_scoped: bool = True,
    org_relation: tuple | None = None,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)
    relation_model, relation_field = org_relation or (None, None)
    delete_roles = delete_roles or write_roles
    register_entity_acl(prefix, read_roles, write_roles, delete_roles)
    exclude_fields = exclude_fields or set()
    read_dep = require_roles(*read_roles)
    write_dep = require_roles(*write_roles)
    delete_dep = require_roles(*delete_roles)

    def get_row(db: Session, row_id: int, user: User):
        row = db.get(model, row_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Qeyd tapılmadı")
        if org_scoped:
            ensure_org_access(model, row, user, db)
            if relation_model is not None and user.role != Role.SUPERADMIN.value and user.organization_id is not None:
                related = db.get(relation_model, getattr(row, relation_field, None))
                if related is None or related.organization_id != user.organization_id:
                    raise HTTPException(status_code=404, detail="Qeyd tapılmadı")
        return row

    @router.get("")
    def list_rows(
        request: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=500),
        q: str | None = None,
        sort: str | None = None,
        include_deleted: bool = False,
        db: Session = Depends(get_db),
        user: User = Depends(read_dep),
    ):
        stmt = select(model)
        if has_column(model, "deleted_at") and not include_deleted:
            stmt = stmt.where(model.deleted_at.is_(None))
        if org_scoped and user.organization_id is not None and user.role != Role.SUPERADMIN.value:
            if model is Organization:
                stmt = stmt.where(model.id == user.organization_id)
            elif relation_model is not None:
                stmt = stmt.join(
                    relation_model, getattr(model, relation_field) == relation_model.id
                ).where(relation_model.organization_id == user.organization_id)
            elif has_column(model, "organization_id"):
                stmt = stmt.where(model.organization_id == user.organization_id)
            elif has_column(model, "employee_id"):
                stmt = stmt.join(Employee, model.employee_id == Employee.id).where(
                    Employee.organization_id == user.organization_id
                )

        if q and search_fields:
            clauses = [getattr(model, field).ilike(f"%{q}%") for field in search_fields]
            stmt = stmt.where(or_(*clauses))

        for key, value in request.query_params.items():
            if key in RESERVED_QUERY or key not in allowed_fields or value == "":
                continue
            if not has_column(model, key):
                continue
            column = getattr(model, key)
            if key in ("is_active", "is_default", "is_paid", "is_taxable", "is_synced_to_payroll"):
                value = value.lower() in ("1", "true", "yes", "bəli", "beli")
            stmt = stmt.where(column == value)

        sort_field = order_by
        sort_dir = "asc"
        if sort:
            sort_field = sort.lstrip("-")
            sort_dir = "desc" if sort.startswith("-") else "asc"
        if has_column(model, sort_field):
            stmt = stmt.order_by(desc(getattr(model, sort_field)) if sort_dir == "desc" else asc(getattr(model, sort_field)))

        total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        rows = list(db.execute(stmt.offset(skip).limit(limit)).scalars().all())
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [serialize(row, exclude_fields) for row in rows],
        }

    @router.get("/{row_id}")
    def get_one(
        row_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(read_dep),
    ):
        row = get_row(db, row_id, user)
        return serialize(row, exclude_fields)

    @router.post("", status_code=201)
    def create_row(
        payload: dict = Body(...),
        db: Session = Depends(get_db),
        user: User = Depends(write_dep),
    ):
        data = {k: v for k, v in payload.items() if k in allowed_fields}
        if org_scoped and has_column(model, "organization_id"):
            if user.organization_id is not None and user.role != Role.SUPERADMIN.value:
                data["organization_id"] = user.organization_id
        data = coerce_payload(model, data)
        if before_create:
            data = before_create(data, db, user)
        data = coerce_payload(model, data)
        if org_scoped and has_column(model, "organization_id") and not data.get("organization_id"):
            raise HTTPException(status_code=400, detail="organization_id tələb olunur")
        if org_scoped:
            _validate_org_employee(model, data, user, db)
            _validate_org_relation(relation_model, relation_field, data, user, db)
        row = model(**data)
        db.add(row)
        try:
            db.flush()
            if after_create:
                after_create(row, db, user)
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=f"Baza məhdudiyyəti pozuldu: {exc.orig}")
        db.refresh(row)
        return serialize(row, exclude_fields)

    @router.patch("/{row_id}")
    def update_row(
        row_id: int,
        payload: dict = Body(...),
        db: Session = Depends(get_db),
        user: User = Depends(write_dep),
    ):
        row = get_row(db, row_id, user)
        data = {k: v for k, v in payload.items() if k in allowed_fields}
        if user.role != Role.SUPERADMIN.value and "organization_id" in data:
            data.pop("organization_id")
        data = coerce_payload(model, data)
        if before_update:
            data = before_update(row, data, db, user)
        data = coerce_payload(model, data)
        if org_scoped:
            _validate_org_employee(model, data, user, db)
            _validate_org_relation(relation_model, relation_field, data, user, db)
        for key, value in data.items():
            setattr(row, key, value)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=f"Baza məhdudiyyəti pozuldu: {exc.orig}")
        db.refresh(row)
        return serialize(row, exclude_fields)

    @router.delete("/{row_id}", status_code=204)
    def delete_row(
        row_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(delete_dep),
    ):
        row = get_row(db, row_id, user)
        if soft_delete and has_column(model, "deleted_at"):
            row.deleted_at = datetime.now(timezone.utc)
        else:
            db.delete(row)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"Qeyd başqa cədvəllərlə əlaqəlidir, silinə bilməz: {exc.orig}",
            )
        return None

    return router
