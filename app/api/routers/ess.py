from calendar import monthrange
from datetime import date, time

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.crud import serialize
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.rbac import ALL_ROLES
from app.models.contract import EmploymentContract
from app.models.employee import Employee
from app.models.leave import LeaveBalance, LeaveRequest, LeaveType, ShortLeaveRequest
from app.models.payroll import PayrollItem, PayrollRun
from app.models.time import Timesheet
from app.models.user import User
from app.services.export_service import generate_employment_reference_pdf, generate_payslip_pdf
from app.services.workflow_service import close_all_steps
from app.services.leave_service import (
    create_leave_request,
    release_leave_request,
)
from app.services.workflow_service import create_step

router = APIRouter(tags=["M14 · ESS Self-Service"])


def _employee(user: User, db: Session) -> Employee:
    if user.employee_id is None:
        raise HTTPException(status_code=400, detail="İstifadəçi işçi profili ilə əlaqələndirilməyib")
    employee = db.get(Employee, user.employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="İşçi profili tapılmadı")
    return employee


@router.get("/ess/me")
def ess_me(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    contract = db.scalar(
        select(EmploymentContract)
        .where(
            EmploymentContract.employee_id == employee.id,
            EmploymentContract.status == "ACTIVE",
        )
        .order_by(EmploymentContract.start_date.desc())
    )
    balances = list(
        db.scalars(
            select(LeaveBalance)
            .where(LeaveBalance.employee_id == employee.id)
            .order_by(LeaveBalance.work_year_start.desc())
        )
    )
    return {
        "employee": serialize(employee),
        "contract": serialize(contract) if contract else None,
        "leave_balances": [serialize(balance) for balance in balances],
    }


@router.get("/ess/payslips")
def ess_payslips(
    limit: int = Query(24, ge=1, le=120),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    rows = db.execute(
        select(PayrollItem, PayrollRun)
        .join(PayrollRun, PayrollRun.id == PayrollItem.payroll_run_id)
        .where(
            PayrollItem.employee_id == employee.id,
            PayrollRun.status.in_(["CALCULATED", "APPROVED", "PAID"]),
        )
        .order_by(PayrollRun.period_year.desc(), PayrollRun.period_month.desc())
        .limit(limit)
    ).all()
    return [
        {
            **serialize(item),
            "period": f"{run.period_year}-{run.period_month:02d}",
            "run_status": run.status,
        }
        for item, run in rows
    ]


@router.get("/ess/payslips/{item_id}/pdf")
def ess_payslip_pdf(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    item = db.get(PayrollItem, item_id)
    if item is None or item.employee_id != employee.id:
        raise HTTPException(status_code=404, detail="Payslip tapılmadı")
    pdf = generate_payslip_pdf(db, item_id)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="payslip-{item_id}.pdf"'},
    )


@router.get("/ess/leave-balances")
def ess_balances(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    rows = list(
        db.scalars(
            select(LeaveBalance)
            .where(LeaveBalance.employee_id == employee.id)
            .order_by(LeaveBalance.work_year_start.desc())
        )
    )
    return [serialize(row) for row in rows]


@router.get("/ess/leave-requests")
def ess_leave_requests(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    rows = list(
        db.scalars(
            select(LeaveRequest)
            .where(LeaveRequest.employee_id == employee.id)
            .order_by(LeaveRequest.start_date.desc())
        )
    )
    return [serialize(row) for row in rows]


@router.post("/ess/leave-requests", status_code=201)
def ess_create_leave(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    leave_type = db.get(LeaveType, payload.get("leave_type_id"))
    if leave_type is None:
        raise HTTPException(status_code=404, detail="Məzuniyyət növü tapılmadı")
    try:
        request = create_leave_request(
            db,
            employee=employee,
            leave_type=leave_type,
            start_date=date.fromisoformat(payload["start_date"]),
            end_date=date.fromisoformat(payload["end_date"]),
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
    return serialize(request)


@router.post("/ess/leave-requests/{request_id}/cancel")
def ess_cancel_leave(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    request = db.get(LeaveRequest, request_id)
    if request is None or request.employee_id != employee.id:
        raise HTTPException(status_code=404, detail="Sorğu tapılmadı")
    if request.status in ("REJECTED", "CANCELLED"):
        raise HTTPException(status_code=400, detail="Sorğu artıq bağlanıb")
    release_leave_request(db, request, "CANCELLED")
    close_all_steps(db, "LEAVE_REQUEST", request.id, "REJECTED")
    db.commit()
    return serialize(request)


@router.post("/ess/short-leaves", status_code=201)
def ess_create_short_leave(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    from datetime import datetime

    def parse_time(value) -> time:
        if isinstance(value, time):
            return value
        text = str(value)
        try:
            return time.fromisoformat(text)
        except ValueError:
            return datetime.fromisoformat(text).time()

    start_time = parse_time(payload["start_time"])
    end_time = parse_time(payload["end_time"])
    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="Bitmə vaxtı başlama vaxtından sonra olmalıdır")
    hours = (datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).seconds / 3600
    if hours > 8.0:
        raise HTTPException(status_code=400, detail="Bir günlük saatlıq icazə 8 saatdan çox ola bilməz")
    leave_date = date.fromisoformat(str(payload["leave_date"]))
    month_start = date(leave_date.year, leave_date.month, 1)
    month_end = date(leave_date.year, leave_date.month, monthrange(leave_date.year, leave_date.month)[1])
    current_sum = db.scalar(
        select(func.coalesce(func.sum(ShortLeaveRequest.hours), 0)).where(
            ShortLeaveRequest.employee_id == employee.id,
            ShortLeaveRequest.leave_date >= month_start,
            ShortLeaveRequest.leave_date <= month_end,
            ShortLeaveRequest.status.in_(["PENDING", "APPROVED"]),
        )
    ) or 0
    if float(current_sum) + hours > 8.0:
        raise HTTPException(
            status_code=400,
            detail=f"Aylıq saatlıq icazə limiti (8 saat) aşılır. Cari istifadə: {current_sum} saat, tələb olunan: {hours:.2f} saat",
        )
    row = ShortLeaveRequest(
        employee_id=employee.id,
        leave_date=leave_date,
        start_time=start_time,
        end_time=end_time,
        hours=round(hours, 2),
        reason=payload.get("reason"),
        status="PENDING",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.get("/ess/timesheets")
def ess_timesheets(
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    stmt = select(Timesheet).where(Timesheet.employee_id == employee.id)
    if year:
        stmt = stmt.where(Timesheet.year == year)
    if month:
        stmt = stmt.where(Timesheet.month == month)
    rows = list(db.scalars(stmt.order_by(Timesheet.year.desc(), Timesheet.month.desc())))
    return [serialize(row) for row in rows]


@router.get("/ess/calendar")
def ess_calendar(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    from app.services.calendar_service import get_month_calendar

    return [serialize(row) for row in get_month_calendar(db, year, month)]


@router.get("/ess/reference.pdf")
def ess_reference_pdf(
    purpose: str = Query("Tələb olunan yerə"),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ALL_ROLES)),
):
    employee = _employee(user, db)
    pdf = generate_employment_reference_pdf(db, employee.id, purpose=purpose)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="arayis-{employee.pin_code}.pdf"'},
    )

