from calendar import monthrange
from datetime import date, datetime, time
from decimal import Decimal
import random

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.crud import build_crud_router, serialize
from app.api.deps import get_current_user, require_roles
from app.core.config import settings
from app.core.database import get_db
from app.core.rbac import ALL_ROLES, Role
from app.models.contract import EmploymentContract
from app.models.employee import Employee
from app.models.organization import Department, Position, StaffingTable
from app.models.time import (
    AttendanceLog,
    EmployeeSchedule,
    ProductionCalendar,
    Timesheet,
    WorkSchedule,
)
from app.models.user import User
from app.services.calendar_service import generate_year_calendar, get_month_calendar
from app.services.timesheet_service import (
    generate_org_timesheets,
    generate_timesheet,
    override_timesheet_day,
)

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


@router.get("/timesheets/matrix")
def timesheet_matrix(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    _check_org(user, org_id)

    sheets = list(
        db.scalars(
            select(Timesheet)
            .where(
                Timesheet.organization_id == org_id,
                Timesheet.year == year,
                Timesheet.month == month,
            )
            .order_by(Timesheet.id)
        )
    )
    if not sheets:
        sheets = generate_org_timesheets(db, org_id, year, month)

    cal_days = get_month_calendar(db, year, month)
    days_meta = [
        {
            "day": d.cal_date.day,
            "date": str(d.cal_date),
            "weekday": ["B.e", "Ç.a", "Ç", "C.a", "C", "Ş", "B"][d.cal_date.weekday()],
            "day_type": d.day_type,
            "norm_hours": float(d.norm_hours_40),
            "description": d.description,
        }
        for d in cal_days
    ]

    employees_data = []
    for sheet in sheets:
        emp = db.get(Employee, sheet.employee_id)
        if not emp or emp.deleted_at is not None:
            continue
        contract = db.get(EmploymentContract, sheet.contract_id)
        dept_name = None
        pos_name = None
        if contract and contract.staffing_id:
            staffing = db.get(StaffingTable, contract.staffing_id)
            if staffing:
                if staffing.department_id:
                    dept = db.get(Department, staffing.department_id)
                    dept_name = dept.name if dept else None
                if staffing.position_id:
                    pos = db.get(Position, staffing.position_id)
                    pos_name = pos.title if pos else None

        employees_data.append(
            {
                "timesheet_id": sheet.id,
                "employee_id": emp.id,
                "name": f"{emp.last_name} {emp.first_name} {emp.father_name or ''}".strip(),
                "pin_code": emp.pin_code,
                "department": dept_name,
                "position": pos_name,
                "status": sheet.status,
                "planned_days": sheet.planned_days,
                "worked_days": sheet.worked_days,
                "regular_hours": float(sheet.regular_hours),
                "overtime_hours": float(sheet.overtime_hours),
                "night_hours": float(sheet.night_hours),
                "holiday_hours": float(sheet.holiday_hours),
                "vacation_days": sheet.vacation_days,
                "sick_days": sheet.sick_days,
                "trip_days": sheet.trip_days,
                "absent_days": sheet.absent_days,
                "daily_records": sheet.daily_records_json or {},
            }
        )

    return {
        "year": year,
        "month": month,
        "days_count": len(cal_days),
        "calendar_days": days_meta,
        "employees": employees_data,
    }


@router.get("/timesheets/{timesheet_id}/daily")
def timesheet_daily(
    timesheet_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    sheet = db.get(Timesheet, timesheet_id)
    if sheet is None:
        raise HTTPException(status_code=404, detail="Tabel tapılmadı")
    _check_org(user, sheet.organization_id)
    emp = db.get(Employee, sheet.employee_id)
    contract = db.get(EmploymentContract, sheet.contract_id)

    if not sheet.daily_records_json and contract:
        sheet = generate_timesheet(db, contract, sheet.year, sheet.month)
        db.commit()

    return {
        "timesheet_id": sheet.id,
        "employee_id": sheet.employee_id,
        "employee_name": f"{emp.last_name} {emp.first_name}" if emp else "İşçi",
        "pin_code": emp.pin_code if emp else "",
        "year": sheet.year,
        "month": sheet.month,
        "status": sheet.status,
        "planned_days": sheet.planned_days,
        "worked_days": sheet.worked_days,
        "regular_hours": float(sheet.regular_hours),
        "overtime_hours": float(sheet.overtime_hours),
        "daily_records": sheet.daily_records_json or {},
    }


@router.post("/timesheets/{timesheet_id}/daily-override")
def timesheet_daily_override(
    timesheet_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE, Role.DEPT_MANAGER)),
):
    sheet = db.get(Timesheet, timesheet_id)
    if sheet is None:
        raise HTTPException(status_code=404, detail="Tabel tapılmadı")
    _check_org(user, sheet.organization_id)
    day_str = payload.get("day")
    if not day_str:
        raise HTTPException(status_code=400, detail="day tələb olunur (YYYY-MM-DD)")
    try:
        day_date = date.fromisoformat(day_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Yanlış tarix formatı (YYYY-MM-DD)")

    worked_hours = Decimal(str(payload.get("worked_hours", 8)))
    code = payload.get("code", "İ")
    notes = payload.get("notes")
    try:
        updated_rec = override_timesheet_day(
            db, sheet, day_date, worked_hours, code, notes, actor_id=user.id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "ok", "record": updated_rec, "timesheet": serialize(sheet)}


@router.post("/attendance/simulate-turnstile")
def simulate_turnstile(
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

    from zoneinfo import ZoneInfo
    tz = ZoneInfo(settings.TIMEZONE)

    cal_days = get_month_calendar(db, year, month)
    workdays = [d for d in cal_days if d.day_type in ("WORKDAY", "SHORT_WORKDAY")]

    employees = list(
        db.scalars(
            select(Employee)
            .where(Employee.organization_id == org_id, Employee.deleted_at.is_(None))
        )
    )
    if not employees:
        return {"created_logs": 0, "message": "Təşkilatda aktiv işçi tapılmadı"}

    created_count = 0
    start_month_dt = datetime.combine(date(year, month, 1), time(0, 0), tzinfo=tz)
    end_month_dt = datetime.combine(date(year, month, monthrange(year, month)[1]), time(23, 59, 59), tzinfo=tz)

    for emp in employees:
        existing = db.scalar(
            select(func.count(AttendanceLog.id)).where(
                AttendanceLog.employee_id == emp.id,
                AttendanceLog.punch_time >= start_month_dt,
                AttendanceLog.punch_time <= end_month_dt,
            )
        )
        if existing and existing > 0:
            continue

        for i, wd in enumerate(workdays):
            d = wd.cal_date
            if (emp.id + i) % 7 == 0:
                in_hour, in_min = 9, random.choice([25, 35, 42])
            else:
                in_hour, in_min = 8, random.choice([48, 52, 55])

            out_hour, out_min = 18, random.choice([3, 7, 12])

            dt_in = datetime.combine(d, time(in_hour, in_min), tzinfo=tz)
            dt_out = datetime.combine(d, time(out_hour, out_min), tzinfo=tz)

            db.add(
                AttendanceLog(
                    employee_id=emp.id,
                    punch_time=dt_in,
                    direction="IN",
                    device_id="TURNSTILE-GATE-01",
                    is_manual=False,
                    raw_payload={"card_uid": f"RFID-{emp.id:04d}", "gate": "Əsas Giriş"},
                )
            )
            db.add(
                AttendanceLog(
                    employee_id=emp.id,
                    punch_time=dt_out,
                    direction="OUT",
                    device_id="TURNSTILE-GATE-02",
                    is_manual=False,
                    raw_payload={"card_uid": f"RFID-{emp.id:04d}", "gate": "Əsas Çıxış"},
                )
            )
            created_count += 2

    db.commit()
    generate_org_timesheets(db, org_id, year, month)
    return {"created_logs": created_count, "message": f"{created_count} turniket qeydi yaradıldı və tabel yeniləndi"}


@router.post("/attendance/import-csv")
def import_attendance_csv(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_WRITE, Role.DEPT_MANAGER)),
):
    import csv
    import io
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(settings.TIMEZONE)

    csv_text = payload.get("csv_text", "")
    if not csv_text.strip():
        raise HTTPException(status_code=400, detail="csv_text tələb olunur")

    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    created = 0
    for row in reader:
        pin = row.get("pin_code") or row.get("pin")
        emp_id = row.get("employee_id")
        emp = None
        if pin:
            emp = db.scalar(select(Employee).where(Employee.pin_code == pin.strip()))
        elif emp_id:
            emp = db.get(Employee, int(emp_id))

        if not emp:
            continue
        _check_org(user, emp.organization_id)

        dt_str = row.get("punch_time") or f"{row.get('date')} {row.get('time')}"
        try:
            pt = datetime.fromisoformat(dt_str.strip())
            if pt.tzinfo is None:
                pt = pt.replace(tzinfo=tz)
        except Exception:
            continue

        direction = (row.get("direction") or "IN").upper().strip()
        device = (row.get("device_id") or "TURNIKET-CSV").strip()

        db.add(
            AttendanceLog(
                employee_id=emp.id,
                punch_time=pt,
                direction=direction,
                device_id=device,
                is_manual=True,
                raw_payload={"source": "CSV_IMPORT"},
            )
        )
        created += 1

    db.commit()
    return {"created": created, "message": f"{created} turniket logu müvəffəqiyyətlə bazaya daxil edildi"}


@router.get("/attendance/today-summary")
def attendance_today_summary(
    organization_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*HR_READ)),
):
    org_id = organization_id or user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="organization_id tələb olunur")
    _check_org(user, org_id)

    from zoneinfo import ZoneInfo
    tz = ZoneInfo(settings.TIMEZONE)
    today = date.today()
    start_dt = datetime.combine(today, time(0, 0), tzinfo=tz)
    end_dt = datetime.combine(today, time(23, 59, 59), tzinfo=tz)

    employees = list(
        db.scalars(
            select(Employee).where(
                Employee.organization_id == org_id, Employee.deleted_at.is_(None)
            )
        )
    )
    punches = list(
        db.scalars(
            select(AttendanceLog)
            .where(
                AttendanceLog.punch_time >= start_dt,
                AttendanceLog.punch_time <= end_dt,
            )
            .order_by(AttendanceLog.punch_time)
        )
    )

    punches_by_emp: dict[int, list[AttendanceLog]] = {}
    for p in punches:
        punches_by_emp.setdefault(p.employee_id, []).append(p)

    present_count = 0
    late_count = 0
    expected_start = datetime.combine(today, time(9, 0), tzinfo=tz)

    emp_list = []
    for emp in employees:
        user_punches = punches_by_emp.get(emp.id, [])
        first_in = next((p for p in user_punches if p.direction == "IN"), None)
        last_out = next((p for p in reversed(user_punches) if p.direction == "OUT"), None)
        is_inside = bool(user_punches and user_punches[-1].direction == "IN")
        is_late = bool(first_in and first_in.punch_time > expected_start)

        if first_in:
            present_count += 1
        if is_late:
            late_count += 1

        emp_list.append(
            {
                "employee_id": emp.id,
                "name": f"{emp.last_name} {emp.first_name}",
                "pin_code": emp.pin_code,
                "first_in": first_in.punch_time.astimezone(tz).strftime("%H:%M") if first_in else None,
                "last_out": last_out.punch_time.astimezone(tz).strftime("%H:%M") if last_out else None,
                "is_inside": is_inside,
                "is_late": is_late,
                "late_minutes": max(0, int((first_in.punch_time - expected_start).total_seconds() // 60)) if is_late else 0,
            }
        )

    return {
        "date": str(today),
        "total_employees": len(employees),
        "present_count": present_count,
        "absent_count": max(0, len(employees) - present_count),
        "late_count": late_count,
        "employees": emp_list,
    }


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
