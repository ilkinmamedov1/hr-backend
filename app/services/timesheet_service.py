from calendar import monthrange
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.contract import EmploymentContract
from app.models.employee import Employee
from app.models.leave import LeaveRequest, LeaveType, SickLeave, ShortLeaveRequest
from app.models.time import AttendanceLog, EmployeeSchedule, Timesheet, WorkSchedule
from app.models.trip import BusinessTrip
from app.services.calendar_service import get_month_calendar
from app.services.payroll_calculator import D

TZ = ZoneInfo(settings.TIMEZONE)


def _schedule_info(db: Session, employee_id: int, org_id: int, month_start: date) -> tuple[Decimal, Decimal]:
    schedule = db.scalar(
        select(WorkSchedule)
        .join(EmployeeSchedule, EmployeeSchedule.work_schedule_id == WorkSchedule.id)
        .where(
            EmployeeSchedule.employee_id == employee_id,
            EmployeeSchedule.effective_from <= month_start,
            (EmployeeSchedule.effective_to.is_(None))
            | (EmployeeSchedule.effective_to >= month_start),
        )
        .order_by(EmployeeSchedule.effective_from.desc())
    )
    if schedule is None:
        schedule = db.scalar(
            select(WorkSchedule).where(
                WorkSchedule.organization_id == org_id, WorkSchedule.is_default.is_(True)
            )
        )
    if schedule is None:
        return Decimal("40"), D(settings.DEFAULT_LUNCH_BREAK_HOURS)
    lunch = D((schedule.shift_rules_json or {}).get("lunch_break_hours", settings.DEFAULT_LUNCH_BREAK_HOURS))
    return D(schedule.weekly_hours), lunch


def _night_hours(start: datetime, end: datetime) -> Decimal:
    if end <= start:
        return Decimal("0")
    total = Decimal("0")
    cursor_day = start.date() - timedelta(days=1)
    last_day = end.date()
    while cursor_day <= last_day:
        window_start = datetime.combine(cursor_day, time(22, 0), tzinfo=TZ)
        window_end = datetime.combine(cursor_day + timedelta(days=1), time(6, 0), tzinfo=TZ)
        overlap_start = max(start, window_start)
        overlap_end = min(end, window_end)
        if overlap_end > overlap_start:
            total += Decimal((overlap_end - overlap_start).total_seconds()) / Decimal("3600")
        cursor_day += timedelta(days=1)
    return total


def _attendance_hours(punches: list[AttendanceLog], lunch_break: Decimal) -> tuple[Decimal, Decimal]:
    if not punches:
        return Decimal("0"), Decimal("0")
    ordered = sorted(punches, key=lambda p: p.punch_time)
    first = ordered[0].punch_time.astimezone(TZ)
    last = ordered[-1].punch_time.astimezone(TZ)
    if last <= first:
        return Decimal("0"), Decimal("0")
    hours = Decimal((last - first).total_seconds()) / Decimal("3600")
    if hours > Decimal("6"):
        hours = max(hours - lunch_break, Decimal("0"))
    night = _night_hours(first, last)
    return hours, night


def generate_timesheet(
    db: Session, contract: EmploymentContract, year: int, month: int
) -> Timesheet:
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])

    timesheet = db.scalar(
        select(Timesheet).where(
            Timesheet.contract_id == contract.id,
            Timesheet.year == year,
            Timesheet.month == month,
        )
    )
    if timesheet and timesheet.status == "LOCKED":
        raise ValueError("Tabel LOCKED statusundadır, dəyişdirilə bilməz")

    employee = db.get(Employee, contract.employee_id)
    weekly_hours, lunch_break = _schedule_info(
        db, contract.employee_id, contract.organization_id, month_start
    )
    use_36 = weekly_hours <= 36
    rows = get_month_calendar(db, year, month)
    workdays = [r for r in rows if r.day_type in ("WORKDAY", "SHORT_WORKDAY")]
    planned_days = len(workdays)
    planned_hours = sum(
        (D(r.norm_hours_36 if use_36 else r.norm_hours_40) for r in workdays), Decimal("0")
    )

    leave_rows = db.execute(
        select(LeaveRequest, LeaveType)
        .join(LeaveType, LeaveType.id == LeaveRequest.leave_type_id)
        .where(
            LeaveRequest.employee_id == contract.employee_id,
            LeaveRequest.status == "APPROVED",
            LeaveRequest.start_date <= month_end,
            LeaveRequest.end_date >= month_start,
        )
    ).all()
    paid_leave_days: set[date] = set()
    unpaid_leave_days: set[date] = set()
    for request, leave_type in leave_rows:
        cursor = max(request.start_date, month_start)
        end = min(request.end_date, month_end)
        while cursor <= end:
            if leave_type.is_paid:
                paid_leave_days.add(cursor)
            else:
                unpaid_leave_days.add(cursor)
            cursor += timedelta(days=1)

    sick_days_set: set[date] = set()
    for sick in db.scalars(
        select(SickLeave).where(
            SickLeave.employee_id == contract.employee_id,
            SickLeave.status == "ACTIVE",
            SickLeave.start_date <= month_end,
            SickLeave.end_date >= month_start,
        )
    ):
        cursor = max(sick.start_date, month_start)
        end = min(sick.end_date, month_end)
        while cursor <= end:
            sick_days_set.add(cursor)
            cursor += timedelta(days=1)

    trip_days_set: set[date] = set()
    for trip in db.scalars(
        select(BusinessTrip).where(
            BusinessTrip.employee_id == contract.employee_id,
            BusinessTrip.status.in_(["APPROVED", "COMPLETED"]),
            BusinessTrip.start_date <= month_end,
            BusinessTrip.end_date >= month_start,
        )
    ):
        cursor = max(trip.start_date, month_start)
        end = min(trip.end_date, month_end)
        while cursor <= end:
            trip_days_set.add(cursor)
            cursor += timedelta(days=1)

    short_leaves_by_day: dict[date, Decimal] = {}
    for short_req in db.scalars(
        select(ShortLeaveRequest).where(
            ShortLeaveRequest.employee_id == contract.employee_id,
            ShortLeaveRequest.status == "APPROVED",
            ShortLeaveRequest.leave_date >= month_start,
            ShortLeaveRequest.leave_date <= month_end,
        )
    ):
        day_date = short_req.leave_date
        short_leaves_by_day[day_date] = short_leaves_by_day.get(day_date, Decimal("0")) + D(short_req.hours)

    start_dt = datetime.combine(month_start, time(0, 0), tzinfo=TZ)
    end_dt = datetime.combine(month_end + timedelta(days=1), time(0, 0), tzinfo=TZ)
    punches_by_day: dict[date, list[AttendanceLog]] = {}
    for log in db.scalars(
        select(AttendanceLog).where(
            AttendanceLog.employee_id == contract.employee_id,
            AttendanceLog.punch_time >= start_dt,
            AttendanceLog.punch_time < end_dt,
        )
    ):
        local_day = log.punch_time.astimezone(TZ).date()
        punches_by_day.setdefault(local_day, []).append(log)

    worked_days = 0
    regular_hours = Decimal("0")
    overtime_hours = Decimal("0")
    night_hours = Decimal("0")
    holiday_hours = Decimal("0")
    vacation_days = 0
    sick_days = 0
    trip_days = 0
    absent_days = 0

    for row in rows:
        day = row.cal_date
        is_workday = row.day_type in ("WORKDAY", "SHORT_WORKDAY")
        day_norm = D(row.norm_hours_36 if use_36 else row.norm_hours_40)
        day_punches = punches_by_day.get(day, [])
        short_hrs = short_leaves_by_day.get(day, Decimal("0"))

        if day in trip_days_set and is_workday:
            trip_days += 1
            worked_days += 1
            regular_hours += day_norm
        elif day in sick_days_set and is_workday:
            sick_days += 1
        elif day in paid_leave_days and is_workday:
            vacation_days += 1
        elif day in unpaid_leave_days and is_workday:
            absent_days += 1
        elif is_workday:
            worked_days += 1
            actual, night = _attendance_hours(day_punches, lunch_break)
            if actual > 0:
                effective_actual = min(actual + short_hrs, day_norm)
                regular_hours += effective_actual
                overtime_hours += max(actual - day_norm, Decimal("0"))
                night_hours += night
            else:
                regular_hours += day_norm
        elif day_punches:
            actual, night = _attendance_hours(day_punches, lunch_break)
            holiday_hours += actual
            night_hours += night

    if timesheet is None:
        timesheet = Timesheet(
            organization_id=contract.organization_id,
            employee_id=contract.employee_id,
            contract_id=contract.id,
            year=year,
            month=month,
        )
        db.add(timesheet)

    timesheet.planned_days = planned_days
    timesheet.worked_days = worked_days
    timesheet.planned_hours = planned_hours.quantize(Decimal("0.01"))
    timesheet.regular_hours = regular_hours.quantize(Decimal("0.01"))
    timesheet.overtime_hours = overtime_hours.quantize(Decimal("0.01"))
    timesheet.night_hours = night_hours.quantize(Decimal("0.01"))
    timesheet.holiday_hours = holiday_hours.quantize(Decimal("0.01"))
    timesheet.vacation_days = vacation_days
    timesheet.sick_days = sick_days
    timesheet.trip_days = trip_days
    timesheet.absent_days = absent_days
    if timesheet.status != "APPROVED":
        timesheet.status = "OPEN"
    db.flush()
    return timesheet


def get_or_generate_timesheet(
    db: Session, contract: EmploymentContract, year: int, month: int
) -> Timesheet:
    timesheet = db.scalar(
        select(Timesheet).where(
            Timesheet.contract_id == contract.id,
            Timesheet.year == year,
            Timesheet.month == month,
        )
    )
    if timesheet:
        return timesheet
    return generate_timesheet(db, contract, year, month)


def generate_org_timesheets(db: Session, organization_id: int, year: int, month: int) -> list[Timesheet]:
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])
    contracts = list(
        db.scalars(
            select(EmploymentContract).where(
                EmploymentContract.organization_id == organization_id,
                EmploymentContract.start_date <= month_end,
                (EmploymentContract.end_date.is_(None)) | (EmploymentContract.end_date >= month_start),
                EmploymentContract.status.in_(["ACTIVE", "TERMINATED"]),
            )
        )
    )
    results = []
    for contract in contracts:
        if contract.status == "TERMINATED" and contract.termination_date and contract.termination_date < month_start:
            continue
        results.append(generate_timesheet(db, contract, year, month))
    db.commit()
    return results
