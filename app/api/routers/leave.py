from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import ALL_ROLES, Role
from app.models.contract import EmploymentContract
from app.models.employee import Employee
from app.models.leave import (
    LeaveBalance,
    LeaveRequest,
    LeaveType,
    ShortLeaveRequest,
    SickLeave,
)
from app.models.user import User
from app.services.calendar_service import get_month_calendar
from app.services.leave_service import (
    approve_leave_request,
    calculate_sick_leave,
    create_leave_request,
    ensure_balances_for_contract,
    release_leave_request,
)
from app.services.workflow_service import close_all_steps, create_step

router = APIRouter(tags=["M06 · Məzuniyyət və İcazələr"])

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
HR_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.ACCOUNTANT, Role.DEPT_MANAGER}
APPROVE_ROLES = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.DEPT_MANAGER}


def _parse_date(value) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _org_filter(stmt, model, user: User):
    if user.role != Role.SUPERADMIN.value:
        if not user.organization_id:
            return stmt.where(False)
        stmt = stmt.where(model.organization_id == user.organization_id)
    return stmt


def _check_org(user: User, organization_id: int | None) -> None:
    if (
        user.role != Role.SUPERADMIN.value
        and (not user.organization_id or organization_id != user.organization_id)
    ):
        raise HTTPException(status_code=404, detail="Qeyd tapılmadı")


def _leave_request_dict(request: LeaveRequest, employee: Employee | None, leave_type: LeaveType | None) -> dict:
    data = serialize(request)
    data["employee_name"] = (
        f"{employee.last_name} {employee.first_name}" if employee else None
    )
    data["pin_code"] = employee.pin_code if employee else None
    data["leave_type"] = leave_type.name if leave_type else None
    data["is_paid"] = leave_type.is_paid if leave_type else None
    return data


@router.post("/leave-balances/initialize")
def initialize_leave_balances(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    contract = db.get(EmploymentContract, payload.get("contract_id"))
    if contract is None:
        raise HTTPException(status_code=404, detail="Müqavilə tapılmadı")
    _check_org(user, contract.organization_id)
    as_of = _parse_date(payload["as_of"]) if payload.get("as_of") else date.today()
    balances = ensure_balances_for_contract(db, contract, as_of)
    db.commit()
    return [serialize(balance) for balance in balances]


@router.get("/leave-requests/calendar")
def leave_calendar(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    month_start = date(year, month, 1)
    rows = list(
        db.scalars(
            select(LeaveRequest).where(
                LeaveRequest.status == "APPROVED",
                LeaveRequest.start_date <= date(year, month, 28),
                LeaveRequest.end_date >= month_start,
            )
        )
    )
    if user.role != Role.SUPERADMIN.value and user.organization_id:
        rows = [r for r in rows if r.organization_id == user.organization_id]
    return [serialize(row) for row in rows]


@router.get("/leave-requests")
def list_leave_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    employee_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    stmt = select(LeaveRequest, Employee, LeaveType).join(
        Employee, Employee.id == LeaveRequest.employee_id
    ).join(LeaveType, LeaveType.id == LeaveRequest.leave_type_id)
    stmt = _org_filter(stmt, LeaveRequest, user)
    if employee_id:
        stmt = stmt.where(LeaveRequest.employee_id == employee_id)
    if status:
        stmt = stmt.where(LeaveRequest.status == status)
    stmt = stmt.order_by(LeaveRequest.start_date.desc()).offset(skip).limit(limit)
    rows = db.execute(stmt).all()
    return [_leave_request_dict(request, employee, leave_type) for request, employee, leave_type in rows]


@router.post("/leave-requests", status_code=201)
def create_request(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE, Role.DEPT_MANAGER)),
):
    employee = db.get(Employee, payload.get("employee_id"))
    leave_type = db.get(LeaveType, payload.get("leave_type_id"))
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    if leave_type is None:
        raise HTTPException(status_code=404, detail="Məzuniyyət növü tapılmadı")
    if user.role != Role.SUPERADMIN.value and user.organization_id != employee.organization_id:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    try:
        request = create_leave_request(
            db,
            employee=employee,
            leave_type=leave_type,
            start_date=_parse_date(payload["start_date"]),
            end_date=_parse_date(payload["end_date"]),
            reason=payload.get("reason"),
        )
        create_step(
            db,
            entity_type="LEAVE_REQUEST",
            entity_id=request.id,
            organization_id=employee.organization_id,
            employee_id=employee.id,
        )
        db.commit()
    except (ValueError, KeyError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(request)
    return _leave_request_dict(request, employee, leave_type)


@router.get("/leave-requests/{request_id}")
def get_leave_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    request = db.get(LeaveRequest, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Sorğu tapılmadı")
    if user.role != Role.SUPERADMIN.value and user.organization_id != request.organization_id:
        raise HTTPException(status_code=404, detail="Sorğu tapılmadı")
    return _leave_request_dict(
        request,
        db.get(Employee, request.employee_id),
        db.get(LeaveType, request.leave_type_id),
    )


@router.post("/leave-requests/{request_id}/approve")
def approve_request(
    request_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*APPROVE_ROLES)),
):
    request = db.get(LeaveRequest, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Sorğu tapılmadı")
    _check_org(user, request.organization_id)
    try:
        approve_leave_request(db, request, user.id)
        close_all_steps(db, "LEAVE_REQUEST", request.id, "APPROVED")
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(request)
    return serialize(request)


@router.post("/leave-requests/{request_id}/reject")
def reject_request(
    request_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*APPROVE_ROLES)),
):
    request = db.get(LeaveRequest, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Sorğu tapılmadı")
    _check_org(user, request.organization_id)
    release_leave_request(db, request, "REJECTED")
    close_all_steps(db, "LEAVE_REQUEST", request.id, "REJECTED")
    db.commit()
    return serialize(request)


@router.post("/leave-requests/{request_id}/cancel")
def cancel_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE, Role.DEPT_MANAGER, Role.EMPLOYEE)),
):
    request = db.get(LeaveRequest, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Sorğu tapılmadı")
    if user.role == Role.EMPLOYEE.value and request.employee_id != user.employee_id:
        raise HTTPException(status_code=403, detail="Bu sorğunu ləğv etmək səlahiyyətiniz yoxdur")
    _check_org(user, request.organization_id)
    release_leave_request(db, request, "CANCELLED")
    close_all_steps(db, "LEAVE_REQUEST", request.id, "REJECTED")
    db.commit()
    return serialize(request)


@router.get("/sick-leaves")
def list_sick_leaves(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    employee_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    stmt = select(SickLeave, Employee).join(Employee, Employee.id == SickLeave.employee_id)
    stmt = _org_filter(stmt, SickLeave, user)
    if employee_id:
        stmt = stmt.where(SickLeave.employee_id == employee_id)
    rows = db.execute(
        stmt.order_by(SickLeave.start_date.desc()).offset(skip).limit(limit)
    ).all()
    return [
        {
            **serialize(sick),
            "employee_name": f"{employee.last_name} {employee.first_name}",
            "pin_code": employee.pin_code,
        }
        for sick, employee in rows
    ]


@router.post("/sick-leaves", status_code=201)
def create_sick_leave(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    employee = db.get(Employee, payload.get("employee_id"))
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    if user.role != Role.SUPERADMIN.value and user.organization_id != employee.organization_id:
        raise HTTPException(status_code=404, detail="İşçi tapılmadı")
    try:
        sick = calculate_sick_leave(
            db,
            employee=employee,
            bulletin_number=payload["bulletin_number"],
            start_date=_parse_date(payload["start_date"]),
            end_date=_parse_date(payload["end_date"]),
            notes=payload.get("notes"),
        )
        db.commit()
    except (ValueError, KeyError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(sick)
    return serialize(sick)


@router.post("/sick-leaves/{sick_id}/cancel")
def cancel_sick_leave(
    sick_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    sick = db.get(SickLeave, sick_id)
    if sick is None:
        raise HTTPException(status_code=404, detail="Bülleten tapılmadı")
    _check_org(user, sick.organization_id)
    sick.status = "CANCELLED"
    db.commit()
    return serialize(sick)


router.include_router(
    build_crud_router(
        model=LeaveType,
        prefix="/leave-types",
        tags=["M06 · Məzuniyyət Növləri"],
        allowed_fields={
            "code", "name", "is_paid", "affects_balance", "max_days_per_year",
            "labor_code_ref", "description",
        },
        read_roles=ALL_ROLES,
        write_roles=HR_WRITE,
        search_fields=("code", "name"),
        org_scoped=False,
    )
)
router.include_router(
    build_crud_router(
        model=LeaveBalance,
        prefix="/leave-balances",
        tags=["M06 · Məzuniyyət Balansı"],
        allowed_fields={
            "employee_id", "contract_id", "work_year_start", "work_year_end",
            "entitled_base_days", "entitled_extra_days", "used_days",
        },
        read_roles=HR_READ,
        write_roles=HR_WRITE,
    )
)
def _validate_short_leave(data: dict, db: Session, user: User) -> dict:
    emp = db.get(Employee, data.get("employee_id"))
    if emp is None:
        raise HTTPException(status_code=400, detail="İşçi tapılmadı")
    _check_org(user, emp.organization_id)
    hours = float(data.get("hours", 0))
    if hours <= 0:
        raise HTTPException(status_code=400, detail="İcazə müddəti 0-dan böyük olmalıdır")
    if hours > 8.0:
        raise HTTPException(status_code=400, detail="Bir günlük saatlıq icazə 8 saatdan çox ola bilməz")
    raw_date = data.get("leave_date")
    leave_date = date.fromisoformat(str(raw_date)) if isinstance(raw_date, (str, date)) else date.today()
    month_start = date(leave_date.year, leave_date.month, 1)
    month_end = date(leave_date.year, leave_date.month, monthrange(leave_date.year, leave_date.month)[1])
    current_sum = db.scalar(
        select(func.coalesce(func.sum(ShortLeaveRequest.hours), 0)).where(
            ShortLeaveRequest.employee_id == emp.id,
            ShortLeaveRequest.leave_date >= month_start,
            ShortLeaveRequest.leave_date <= month_end,
            ShortLeaveRequest.status.in_(["PENDING", "APPROVED"]),
        )
    ) or 0
    if float(current_sum) + hours > 8.0:
        raise HTTPException(
            status_code=400,
            detail=f"Aylıq saatlıq icazə limiti (8 saat) aşılır. Cari istifadə: {current_sum} saat, tələb olunan: {hours} saat",
        )
    return data


router.include_router(
    build_crud_router(
        model=ShortLeaveRequest,
        prefix="/short-leaves",
        tags=["M06 · Saatlıq İcazələr"],
        allowed_fields={
            "employee_id", "leave_date", "start_time", "end_time", "hours",
            "reason", "status", "approved_by",
        },
        read_roles=HR_READ,
        write_roles=HR_WRITE,
        order_by="leave_date",
        before_create=_validate_short_leave,
    )
)
