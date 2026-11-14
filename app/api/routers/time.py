from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.rbac import ALL_ROLES, Role
from app.models.employee import Employee
from app.models.time import (
    AttendanceLog,
    EmployeeSchedule,
    ProductionCalendar,
    Timesheet,
    WorkSchedule,
)
from app.models.user import User
from app.services.calendar_service import generate_year_calendar, get_month_calendar
from app.services.timesheet_service import generate_org_timesheets, generate_timesheet

router = APIRouter(tags=["M05 · İş Vaxtı və Tabel"])

HR_WRITE = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST}
HR_READ = {Role.SUPERADMIN, Role.HR_DIRECTOR, Role.HR_SPECIALIST, Role.ACCOUNTANT, Role.DEPT_MANAGER}


def _check_org(user: User, organization_id: int | None) -> None:
    if (
        user.role != Role.SUPERADMIN.value
        and user.organization_id is not None
        and organization_id != user.organization_id
    ):
        raise HTTPException(status_code=404, detail="Qeyd tapılmadı")


@router.get("/production-calendar")
def list_calendar(
    year: int = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = list(
        db.scalars(
            select(ProductionCalendar)
            .where(ProductionCalendar.year == year)
            .order_by(ProductionCalendar.cal_date)
        )
    )
    if not rows:
        generate_year_calendar(db, year)
        rows = list(
            db.scalars(
                select(ProductionCalendar)
                .where(ProductionCalendar.year == year)
                .order_by(ProductionCalendar.cal_date)
            )
        )
    return [serialize(row) for row in rows]


@router.get("/production-calendar/month")
def get_calendar_month(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = get_month_calendar(db, year, month)
    workdays = [row for row in rows if row.day_type in ("WORKDAY", "SHORT_WORKDAY")]
    return {
        "year": year,
        "month": month,
        "workdays": len(workdays),
        "norm_hours_40": float(sum((Decimal(row.norm_hours_40) for row in rows), Decimal("0"))),
        "norm_hours_36": float(sum((Decimal(row.norm_hours_36) for row in rows), Decimal("0"))),
        "days": [serialize(row) for row in rows],
    }


@router.post("/production-calendar/generate")
def generate_calendar(
    year: int = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    rows = generate_year_calendar(db, year)
    return {"year": year, "generated_days": rows}


@router.patch("/production-calendar/{cal_date}")
def update_calendar_day(
    cal_date: date,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    row = db.get(ProductionCalendar, cal_date)
    if row is None:
        raise HTTPException(status_code=404, detail="Təqvim günü tapılmadı")
    for field in ("day_type", "norm_hours_40", "norm_hours_36", "description"):
        if field in payload:
            setattr(row, field, payload[field])
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.post("/attendance/import")
def import_attendance(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE, Role.DEPT_MANAGER)),
):
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise HTTPException(status_code=400, detail="records massiv olmalıdır")
    created = 0
    for record in records:
        employee_id = record.get("employee_id")
        punch_time = record.get("punch_time")
        if not employee_id or not punch_time:
            continue
        employee = db.get(Employee, employee_id)
        if employee is None:
            raise HTTPException(status_code=404, detail="İşçi tapılmadı")
        _check_org(user, employee.organization_id)
        log = AttendanceLog(
            employee_id=employee_id,
            punch_time=datetime.fromisoformat(punch_time) if isinstance(punch_time, str) else punch_time,
            direction=record.get("direction", "IN"),
            device_id=record.get("device_id"),
            is_manual=bool(record.get("is_manual", False)),
            raw_payload=record.get("raw_payload", {}),
        )
        db.add(log)
        created += 1
    db.commit()
    return {"created": created}


@router.post("/timesheets/generate")
def generate_timesheets(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    _check_org(user, org_id)
    try:
        rows = generate_org_timesheets(db, org_id, year, month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"generated": len(rows), "timesheet_ids": [row.id for row in rows]}


@router.post("/timesheets/{timesheet_id}/approve")
def approve_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    timesheet = db.get(Timesheet, timesheet_id)
    if timesheet is None:
        raise HTTPException(status_code=404, detail="Tabel tapılmadı")
    _check_org(user, timesheet.organization_id)
    timesheet.status = "APPROVED"
    timesheet.approved_by = user.id
    db.commit()
    return serialize(timesheet)


@router.post("/timesheets/{timesheet_id}/lock")
def lock_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE)),
):
    timesheet = db.get(Timesheet, timesheet_id)
    if timesheet is None:
        raise HTTPException(status_code=404, detail="Tabel tapılmadı")
    _check_org(user, timesheet.organization_id)
    timesheet.status = "LOCKED"
    db.commit()
    return serialize(timesheet)


router.include_router(
    build_crud_router(
        model=WorkSchedule,
        prefix="/work-schedules",
        tags=["M05 · İş Qrafikləri"],
        allowed_fields={
            "organization_id", "name", "schedule_type", "weekly_hours", "shift_rules_json", "is_default",
        },
        read_roles=ALL_ROLES,
        write_roles=HR_WRITE,
        search_fields=("name",),
    )
)
router.include_router(
    build_crud_router(
        model=EmployeeSchedule,
        prefix="/employee-schedules",
        tags=["M05 · Fərdi Qrafiklər"],
        allowed_fields={"employee_id", "work_schedule_id", "effective_from", "effective_to"},
        read_roles=HR_READ,
        write_roles=HR_WRITE,
    )
)
router.include_router(
    build_crud_router(
        model=AttendanceLog,
        prefix="/attendance",
        tags=["M05 · Davamiyyət / Turniket"],
        allowed_fields={"employee_id", "punch_time", "direction", "device_id", "is_manual", "raw_payload"},
        read_roles=HR_READ,
        write_roles=HR_WRITE,
        order_by="punch_time",
    )
)
router.include_router(
    build_crud_router(
        model=Timesheet,
        prefix="/timesheets",
        tags=["M05 · Aylıq Tabel (T-13)"],
        allowed_fields={
            "organization_id", "employee_id", "contract_id", "year", "month", "planned_days",
            "worked_days", "planned_hours", "regular_hours", "overtime_hours", "night_hours",
            "holiday_hours", "vacation_days", "sick_days", "trip_days", "absent_days",
            "status", "approved_by",
        },
        read_roles=HR_READ,
        write_roles=HR_WRITE,
        order_by="id",
    )
)
