from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.contract import EmploymentContract
from app.models.employee import Employee, EmployeeFamilyMember
from app.models.leave import LeaveBalance, LeaveRequest, LeaveType, SickLeave
from app.models.organization import Position, StaffingTable
from app.models.payroll import PayrollItem, PayrollRun
from app.models.time import ProductionCalendar
from app.services.payroll_calculator import (
    D,
    average_daily_wage,
    calculate_sick_leave_amounts,
    q,
    sick_leave_coverage_pct,
)


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def work_year_period(contract_start: date, target: date) -> tuple[date, date]:
    start = contract_start
    while True:
        end = add_years(start, 1) - timedelta(days=1)
        if start <= target <= end:
            return start, end
        if target < start:
            previous = add_years(start, -1)
            return previous, start - timedelta(days=1)
        start = add_years(start, 1)


def total_tenure_years(employee: Employee, contract: EmploymentContract, at_date: date) -> Decimal:
    previous = D(employee.total_insurance_tenure_years)
    current = Decimal(max((at_date - contract.start_date).days, 0)) / Decimal("365.25")
    return previous + current


def extra_vacation_days(
    db: Session, employee: Employee, contract: EmploymentContract, at_date: date
) -> Decimal:
    extra = Decimal("0")
    tenure = total_tenure_years(employee, contract, at_date)
    if tenure >= 15:
        extra += 6
    elif tenure >= 10:
        extra += 4
    elif tenure >= 5:
        extra += 2

    cutoff = at_date - timedelta(days=365 * 14 + 4)
    children = db.scalar(
        select(func.count(EmployeeFamilyMember.id)).where(
            EmployeeFamilyMember.employee_id == employee.id,
            EmployeeFamilyMember.relation == "CHILD",
            EmployeeFamilyMember.birth_date.isnot(None),
            EmployeeFamilyMember.birth_date >= cutoff,
            EmployeeFamilyMember.birth_date <= at_date,
        )
    ) or 0
    if children >= 3:
        extra += 5
    elif children >= 2:
        extra += 2

    staffing = db.get(StaffingTable, contract.staffing_id)
    if staffing and D(staffing.harmful_work_bonus_pct) > 0:
        extra += 6
    return extra


def base_vacation_days(db: Session, contract: EmploymentContract) -> Decimal:
    if contract.annual_leave_days:
        return D(contract.annual_leave_days)
    staffing = db.get(StaffingTable, contract.staffing_id)
    if staffing:
        position = db.get(Position, staffing.position_id)
        if position and position.annual_leave_days:
            return D(position.annual_leave_days)
    return D(settings.DEFAULT_ANNUAL_LEAVE_DAYS)


def recalc_balance(db: Session, balance: LeaveBalance) -> LeaveBalance:
    employee = db.get(Employee, balance.employee_id)
    contract = db.get(EmploymentContract, balance.contract_id)
    if employee and contract:
        balance.entitled_base_days = base_vacation_days(db, contract)
        balance.entitled_extra_days = extra_vacation_days(db, employee, contract, balance.work_year_start)

    used = db.scalar(
        select(func.coalesce(func.sum(LeaveRequest.paid_days), 0))
        .join(LeaveType, LeaveType.id == LeaveRequest.leave_type_id)
        .where(
            LeaveRequest.employee_id == balance.employee_id,
            LeaveRequest.status == "APPROVED",
            LeaveType.affects_balance.is_(True),
            LeaveRequest.start_date >= balance.work_year_start,
            LeaveRequest.start_date <= balance.work_year_end,
        )
    )
    balance.used_days = D(used)
    return balance


def ensure_balance_for(
    db: Session, contract: EmploymentContract, target: date
) -> LeaveBalance:
    start, end = work_year_period(contract.start_date, target)
    balance = db.scalar(
        select(LeaveBalance).where(
            LeaveBalance.contract_id == contract.id,
            LeaveBalance.work_year_start == start,
        )
    )
    if balance is None:
        balance = LeaveBalance(
            employee_id=contract.employee_id,
            contract_id=contract.id,
            work_year_start=start,
            work_year_end=end,
            entitled_base_days=Decimal("0"),
            entitled_extra_days=Decimal("0"),
            used_days=Decimal("0"),
        )
        db.add(balance)
        db.flush()
    recalc_balance(db, balance)
    return balance


def ensure_balances_for_contract(
    db: Session, contract: EmploymentContract, as_of: date | None = None
) -> list[LeaveBalance]:
    as_of = as_of or date.today()
    if contract.termination_date and contract.termination_date < as_of:
        as_of = contract.termination_date
    current = contract.start_date
    balances = []
    guard = 0
    while current <= as_of and guard < 60:
        balances.append(ensure_balance_for(db, contract, current))
        current = add_years(current, 1)
        guard += 1
    return balances


def all_balances_for_employee(db: Session, employee_id: int) -> list[LeaveBalance]:
    return list(
        db.scalars(
            select(LeaveBalance)
            .where(LeaveBalance.employee_id == employee_id)
            .order_by(LeaveBalance.work_year_start.desc())
        )
    )


def paid_days_between(db: Session, start: date, end: date) -> tuple[int, int, int]:
    rows = list(
        db.scalars(
            select(ProductionCalendar).where(
                ProductionCalendar.cal_date >= start,
                ProductionCalendar.cal_date <= end,
            )
        )
    )
    if not rows:
        from app.services.calendar_service import get_month_calendar

        cursor = date(start.year, start.month, 1)
        while cursor <= end:
            get_month_calendar(db, cursor.year, cursor.month)
            cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
        rows = list(
            db.scalars(
                select(ProductionCalendar).where(
                    ProductionCalendar.cal_date >= start,
                    ProductionCalendar.cal_date <= end,
                )
            )
        )
    holiday_count = sum(1 for r in rows if r.day_type in ("HOLIDAY", "MOURNING"))
    workday_count = sum(1 for r in rows if r.day_type in ("WORKDAY", "SHORT_WORKDAY"))
    calendar_days = (end - start).days + 1
    return calendar_days, calendar_days - holiday_count, workday_count


def create_leave_request(
    db: Session,
    *,
    employee: Employee,
    leave_type: LeaveType,
    start_date: date,
    end_date: date,
    reason: str | None = None,
) -> LeaveRequest:
    if end_date < start_date:
        raise ValueError("Bitiş tarixi başlanğıc tarixindən əvvəl ola bilməz")

    contract = db.scalar(
        select(EmploymentContract).where(
            EmploymentContract.employee_id == employee.id,
            EmploymentContract.organization_id == employee.organization_id,
            EmploymentContract.status == "ACTIVE",
        )
    )
    if contract is None:
        raise ValueError("İşçinin aktiv əmək müqaviləsi yoxdur")

    calendar_days, paid_days, _ = paid_days_between(db, start_date, end_date)
    if leave_type.max_days_per_year and calendar_days > leave_type.max_days_per_year:
        raise ValueError(
            f"{leave_type.name} üzrə maksimum {leave_type.max_days_per_year} gün icazə verilir"
        )

    if leave_type.affects_balance and leave_type.is_paid:
        balance = ensure_balance_for(db, contract, start_date)
        remaining = D(balance.entitled_base_days) + D(balance.entitled_extra_days) - D(balance.used_days)
        if paid_days > remaining:
            raise ValueError(
                f"Məzuniyyət balansı kifayət etmir: qalıq {remaining} gün, tələb {paid_days} gün"
            )

    request = LeaveRequest(
        organization_id=employee.organization_id,
        employee_id=employee.id,
        leave_type_id=leave_type.id,
        start_date=start_date,
        end_date=end_date,
        calendar_days=calendar_days,
        paid_days=paid_days,
        excluded_holidays=calendar_days - paid_days,
        status="PENDING",
        reason=reason,
    )
    db.add(request)
    db.flush()
    return request


def approve_leave_request(db: Session, request: LeaveRequest, approver_id: int | None) -> LeaveRequest:
    if request.status == "APPROVED":
        return request
    employee = db.get(Employee, request.employee_id)
    leave_type = db.get(LeaveType, request.leave_type_id)
    contract = db.scalar(
        select(EmploymentContract).where(
            EmploymentContract.employee_id == employee.id, EmploymentContract.status == "ACTIVE"
        )
    )
    if contract and leave_type.affects_balance and leave_type.is_paid:
        balance = ensure_balance_for(db, contract, request.start_date)
        remaining = D(balance.entitled_base_days) + D(balance.entitled_extra_days) - D(balance.used_days)
        if D(request.paid_days) > remaining:
            raise ValueError(f"Məzuniyyət balansı kifayət etmir: qalıq {remaining} gün")

    request.status = "APPROVED"
    request.approved_by = approver_id
    request.approved_at = date.today()
    db.flush()
    if contract:
        ensure_balance_for(db, contract, request.start_date)
    return request


def release_leave_request(db: Session, request: LeaveRequest, status: str = "CANCELLED") -> LeaveRequest:
    request.status = status
    db.flush()
    contract = db.scalar(
        select(EmploymentContract).where(
            EmploymentContract.employee_id == request.employee_id,
            EmploymentContract.status == "ACTIVE",
        )
    )
    if contract:
        ensure_balance_for(db, contract, request.start_date)
    return request


def approved_leave_paid_days_in_month(
    db: Session, employee_id: int, year: int, month: int
) -> tuple[Decimal, Decimal]:
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])
    rows = db.execute(
        select(LeaveRequest, LeaveType)
        .join(LeaveType, LeaveType.id == LeaveRequest.leave_type_id)
        .where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status == "APPROVED",
            LeaveRequest.start_date <= month_end,
            LeaveRequest.end_date >= month_start,
        )
    ).all()
    paid = Decimal("0")
    unpaid = Decimal("0")
    for request, leave_type in rows:
        overlap_start = max(request.start_date, month_start)
        overlap_end = min(request.end_date, month_end)
        _, paid_days, _ = paid_days_between(db, overlap_start, overlap_end)
        if leave_type.is_paid:
            paid += Decimal(paid_days)
        else:
            unpaid += Decimal(paid_days)
    return paid, unpaid


def average_monthly_wage(
    db: Session,
    employee_id: int,
    ref_date: date,
    fallback_contract: EmploymentContract | None = None,
    months: int = 12,
) -> tuple[Decimal, int]:
    ref_month_start = date(ref_date.year, ref_date.month, 1)
    start_month = ref_month_start - relativedelta(months=months)

    rows = db.execute(
        select(
            PayrollRun.period_year,
            PayrollRun.period_month,
            PayrollItem.gross_total,
        )
        .join(PayrollRun, PayrollRun.id == PayrollItem.payroll_run_id)
        .where(
            PayrollItem.employee_id == employee_id,
            PayrollRun.status.in_(["CALCULATED", "APPROVED", "PAID"]),
            func.make_date(PayrollRun.period_year, PayrollRun.period_month, 1) >= start_month,
            func.make_date(PayrollRun.period_year, PayrollRun.period_month, 1) < ref_month_start,
        )
    ).all()

    totals: dict[tuple[int, int], Decimal] = {}
    for year, month, gross in rows:
        totals[(year, month)] = totals.get((year, month), Decimal("0")) + D(gross)

    if not totals:
        if fallback_contract:
            return D(fallback_contract.gross_salary), 1
        return Decimal("0"), 0

    return sum(totals.values(), Decimal("0")), len(totals)


def vacation_daily_wage(
    db: Session, employee_id: int, ref_date: date, contract: EmploymentContract
) -> Decimal:
    total, count = average_monthly_wage(db, employee_id, ref_date, contract)
    return average_daily_wage(total, count)


def calculate_sick_leave(
    db: Session,
    *,
    employee: Employee,
    bulletin_number: str,
    start_date: date,
    end_date: date,
    notes: str | None = None,
) -> SickLeave:
    if end_date < start_date:
        raise ValueError("Bitiş tarixi başlanğıc tarixindən əvvəl ola bilməz")
    contract = db.scalar(
        select(EmploymentContract).where(
            EmploymentContract.employee_id == employee.id,
            EmploymentContract.status == "ACTIVE",
        )
    )
    if contract is None:
        raise ValueError("İşçinin aktiv əmək müqaviləsi yoxdur")

    total_days = (end_date - start_date).days + 1
    tenure = total_tenure_years(employee, contract, start_date)
    coverage = sick_leave_coverage_pct(tenure)
    avg_total, avg_count = average_monthly_wage(db, employee.id, start_date, contract)
    avg_monthly = avg_total / avg_count if avg_count else D(contract.gross_salary)
    amounts = calculate_sick_leave_amounts(
        total_days=total_days, average_monthly_wage=avg_monthly, coverage_pct=coverage
    )

    sick = SickLeave(
        organization_id=employee.organization_id,
        employee_id=employee.id,
        bulletin_number=bulletin_number,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        employer_paid_days=amounts["employer_paid_days"],
        dsmf_paid_days=amounts["dsmf_paid_days"],
        coverage_pct=coverage,
        average_daily_wage=amounts["average_daily_wage"],
        employer_amount=amounts["employer_amount"],
        dsmf_amount=amounts["dsmf_amount"],
        calculated_amount=amounts["calculated_amount"],
        status="ACTIVE",
        notes=notes,
    )
    db.add(sick)
    db.flush()
    return sick


def sick_amount_in_month(
    db: Session, employee_id: int, year: int, month: int
) -> tuple[Decimal, Decimal]:
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])
    leaves = list(
        db.scalars(
            select(SickLeave).where(
                SickLeave.employee_id == employee_id,
                SickLeave.status == "ACTIVE",
                SickLeave.start_date <= month_end,
                SickLeave.end_date >= month_start,
            )
        )
    )
    amount = Decimal("0")
    days = Decimal("0")
    for leave in leaves:
        overlap_start = max(leave.start_date, month_start)
        overlap_end = min(leave.end_date, month_end)
        overlap_days = (overlap_end - overlap_start).days + 1
        share = Decimal(overlap_days) / Decimal(max(leave.total_days, 1))
        amount += D(leave.calculated_amount) * share
        days += Decimal(overlap_days)
    return q(amount), days


def final_settlement_preview(
    db: Session, employee_id: int, termination_date: date, reason: str | None = None
) -> dict:
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise ValueError("İşçi tapılmadı")
    contract = db.scalar(
        select(EmploymentContract).where(
            EmploymentContract.employee_id == employee_id, EmploymentContract.status == "ACTIVE"
        )
    )
    if contract is None:
        raise ValueError("Aktiv müqavilə tapılmadı")

    ensure_balances_for_contract(db, contract, termination_date)
    balances = all_balances_for_employee(db, employee_id)
    unused_days = sum(
        (
            D(b.entitled_base_days) + D(b.entitled_extra_days) - D(b.used_days)
            for b in balances
            if b.contract_id == contract.id and b.work_year_start <= termination_date
        ),
        Decimal("0"),
    )
    daily = vacation_daily_wage(db, employee_id, termination_date, contract)
    vacation_compensation = q(max(unused_days, Decimal("0")) * daily)

    total, count = average_monthly_wage(db, employee_id, termination_date, contract)
    average_monthly = total / count if count else D(contract.gross_salary)
    severance = Decimal("0")
    if reason in ("STAFF_REDUCTION", "LIQUIDATION"):
        severance = q(average_monthly * D(settings.DEFAULT_SEVERANCE_MONTHS))

    return {
        "employee_id": employee_id,
        "contract_id": contract.id,
        "termination_date": termination_date.isoformat(),
        "unused_vacation_days": float(q(unused_days)),
        "average_daily_wage": float(q(daily)),
        "vacation_compensation": float(vacation_compensation),
        "average_monthly_wage": float(q(average_monthly)),
        "severance_pay": float(severance),
        "total_compensation": float(q(vacation_compensation + severance)),
    }
