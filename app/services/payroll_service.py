from calendar import monthrange
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.contract import EmploymentContract
from app.models.employee import Employee, EmployeeTaxExemption
from app.models.organization import Organization
from app.models.payroll import (
    EmployeePayComponent,
    PayrollComponent,
    PayrollItem,
    PayrollItemDetail,
    PayrollRun,
    TaxSocialRateHistory,
)
from app.models.performance import KpiEvaluation
from app.services.leave_service import (
    approved_leave_paid_days_in_month,
    sick_amount_in_month,
    vacation_daily_wage,
    average_monthly_wage,
)
from app.services.payroll_calculator import D, calculate_taxes, q
from app.services.timesheet_service import get_or_generate_timesheet

DEFAULT_FLAGS = {
    "BASE": {"taxable": True, "dsmf": True, "its": True, "unemployment": True},
    "OVERTIME": {"taxable": True, "dsmf": True, "its": True, "unemployment": True},
    "NIGHT": {"taxable": True, "dsmf": True, "its": True, "unemployment": True},
    "HOLIDAY": {"taxable": True, "dsmf": True, "its": True, "unemployment": True},
    "VACATION": {"taxable": True, "dsmf": True, "its": True, "unemployment": True},
    "SICK": {"taxable": True, "dsmf": False, "its": False, "unemployment": False},
    "BONUS_KPI": {"taxable": True, "dsmf": True, "its": True, "unemployment": True},
}


def get_rate_rules(db: Session, sector_type: str, on_date: date) -> dict:
    row = db.scalar(
        select(TaxSocialRateHistory)
        .where(
            TaxSocialRateHistory.sector_type == sector_type,
            TaxSocialRateHistory.effective_from <= on_date,
            (TaxSocialRateHistory.effective_to.is_(None))
            | (TaxSocialRateHistory.effective_to >= on_date),
        )
        .order_by(TaxSocialRateHistory.effective_from.desc())
    )
    if row is None:
        raise ValueError(
            f"{sector_type} sektoru üçün {on_date} tarixində qüvvədə olan vergi dərəcələri tapılmadı"
        )
    return row.rules_json


def _active_contracts(db: Session, organization_id: int, year: int, month: int) -> list[EmploymentContract]:
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
    return [
        c
        for c in contracts
        if not (
            c.status == "TERMINATED"
            and c.termination_date
            and c.termination_date < month_start
        )
    ]


def _exemption_total(db: Session, employee_id: int, year: int, month: int) -> Decimal:
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])
    total = db.scalar(
        select(func.coalesce(func.sum(EmployeeTaxExemption.monthly_amount), 0)).where(
            EmployeeTaxExemption.employee_id == employee_id,
            EmployeeTaxExemption.valid_from <= month_end,
            (EmployeeTaxExemption.valid_to.is_(None))
            | (EmployeeTaxExemption.valid_to >= month_start),
        )
    )
    return D(total)


def _employee_components(db: Session, employee_id: int, year: int, month: int):
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])
    return db.execute(
        select(EmployeePayComponent, PayrollComponent)
        .join(PayrollComponent, PayrollComponent.id == EmployeePayComponent.component_id)
        .where(
            EmployeePayComponent.employee_id == employee_id,
            EmployeePayComponent.valid_from <= month_end,
            (EmployeePayComponent.valid_to.is_(None))
            | (EmployeePayComponent.valid_to >= month_start),
        )
    ).all()


def _kpi_bonus(db: Session, employee_id: int, year: int, month: int, base_salary: Decimal):
    period = f"{year}-{month:02d}"
    evaluations = list(
        db.scalars(
            select(KpiEvaluation).where(
                KpiEvaluation.employee_id == employee_id,
                KpiEvaluation.period_code == period,
                KpiEvaluation.is_synced_to_payroll.is_(False),
            )
        )
    )
    bonus = Decimal("0")
    for evaluation in evaluations:
        multiplier = D(evaluation.bonus_multiplier)
        if multiplier > 1:
            bonus += base_salary * (multiplier - 1)
    return q(bonus), evaluations


def calculate_payroll_run(db: Session, run: PayrollRun, actor_id: int | None = None) -> PayrollRun:
    if run.status in ("APPROVED", "PAID"):
        raise ValueError("Təsdiqlənmiş/ödənilmiş əməkhaqqı hesablaması dəyişdirilə bilməz")

    organization = db.get(Organization, run.organization_id)
    if organization is None:
        raise ValueError("Təşkilat tapılmadı")

    year, month = run.period_year, run.period_month
    month_end = date(year, month, monthrange(year, month)[1])
    rules = get_rate_rules(db, organization.sector_type, month_end)
    contracts = _active_contracts(db, run.organization_id, year, month)

    period_code = f"{year}-{month:02d}"
    db.execute(
        update(KpiEvaluation)
        .where(
            KpiEvaluation.period_code == period_code,
            KpiEvaluation.is_synced_to_payroll.is_(True),
            KpiEvaluation.employee_id.in_(
                select(Employee.id).where(Employee.organization_id == run.organization_id)
            ),
        )
        .values(is_synced_to_payroll=False)
    )
    db.execute(delete(PayrollItem).where(PayrollItem.payroll_run_id == run.id))
    db.flush()

    totals = {
        "gross": Decimal("0"),
        "net": Decimal("0"),
        "income_tax": Decimal("0"),
        "dsmf": Decimal("0"),
        "its": Decimal("0"),
        "unemployment": Decimal("0"),
    }
    synced_evaluations: list[KpiEvaluation] = []

    for contract in contracts:
        employee = db.get(Employee, contract.employee_id)
        if employee is None or employee.deleted_at is not None:
            continue
        if contract.status == "TERMINATED" and contract.termination_date:
            if contract.termination_date < date(year, month, 1):
                continue

        timesheet = get_or_generate_timesheet(db, contract, year, month)
        planned_days = max(timesheet.planned_days, 1)
        planned_hours = D(timesheet.planned_hours)
        if planned_hours <= 0:
            planned_hours = D("176")

        monthly_salary = D(contract.gross_salary)
        if contract.salary_type == "HOURLY":
            hourly_rate = monthly_salary
            base_gross = q(hourly_rate * D(timesheet.regular_hours))
        else:
            hourly_rate = monthly_salary / planned_hours
            base_gross = q(monthly_salary * D(timesheet.worked_days) / D(planned_days))

        org_settings = organization.settings_json or {}
        overtime_multiplier = D(org_settings.get("overtime_multiplier", settings.DEFAULT_OVERTIME_MULTIPLIER))
        night_bonus_pct = D(org_settings.get("night_bonus_pct", settings.DEFAULT_NIGHT_BONUS_PCT))
        holiday_multiplier = D(org_settings.get("holiday_multiplier", settings.DEFAULT_HOLIDAY_MULTIPLIER))

        overtime_pay = q(hourly_rate * D(timesheet.overtime_hours) * overtime_multiplier)
        night_pay = q(hourly_rate * D(timesheet.night_hours) * night_bonus_pct)
        holiday_pay = q(hourly_rate * D(timesheet.holiday_hours) * holiday_multiplier)

        vacation_days, _unpaid = approved_leave_paid_days_in_month(db, employee.id, year, month)
        daily = vacation_daily_wage(db, employee.id, date(year, month, 1), contract)
        vacation_pay = q(daily * vacation_days)

        sick_pay, sick_days = sick_amount_in_month(db, employee.id, year, month)
        kpi_bonus, evaluations = _kpi_bonus(db, employee.id, year, month, monthly_salary)
        synced_evaluations.extend(evaluations)

        taxable_base = Decimal("0")
        dsmf_base = Decimal("0")
        its_base = Decimal("0")
        unemployment_base = Decimal("0")
        gross_total = Decimal("0")
        details: list[dict] = []

        def add_component(code: str, amount: Decimal, note: str, flags: dict | None = None, base=None, qty=None, rate=None):
            nonlocal taxable_base, dsmf_base, its_base, unemployment_base, gross_total
            amount = q(amount)
            if amount == 0:
                return
            gross_total += amount
            f = flags or DEFAULT_FLAGS.get(
                code, {"taxable": True, "dsmf": True, "its": True, "unemployment": True}
            )
            if f.get("taxable", True):
                taxable_base += amount
            if f.get("dsmf", True):
                dsmf_base += amount
            if f.get("its", True):
                its_base += amount
            if f.get("unemployment", True):
                unemployment_base += amount
            details.append(
                {
                    "component_code": code,
                    "direction": "EARNING",
                    "amount": amount,
                    "base_amount": q(base) if base is not None else None,
                    "quantity": D(qty) if qty is not None else None,
                    "rate": D(rate) if rate is not None else None,
                    "calc_formula_note": note,
                }
            )

        add_component(
            "BASE",
            base_gross,
            f"Əsas əməkhaqqı: {monthly_salary} x {timesheet.worked_days}/{planned_days} iş günü",
            base=monthly_salary,
            qty=timesheet.worked_days,
        )
        add_component(
            "OVERTIME",
            overtime_pay,
            f"İş vaxtından artıq: {timesheet.overtime_hours} saat x {overtime_multiplier}",
            base=hourly_rate,
            qty=timesheet.overtime_hours,
            rate=overtime_multiplier,
        )
        add_component(
            "NIGHT",
            night_pay,
            f"Gecə vaxtı əlavəsi: {timesheet.night_hours} saat x {night_bonus_pct}",
            base=hourly_rate,
            qty=timesheet.night_hours,
            rate=night_bonus_pct,
        )
        add_component(
            "HOLIDAY",
            holiday_pay,
            f"Bayram/istirahət günü işi: {timesheet.holiday_hours} saat x {holiday_multiplier}",
            base=hourly_rate,
            qty=timesheet.holiday_hours,
            rate=holiday_multiplier,
        )
        add_component(
            "VACATION",
            vacation_pay,
            f"Məzuniyyət pulu: {vacation_days} təqvim günü x gündəlik {q(daily)}",
            base=daily,
            qty=vacation_days,
            rate=daily,
        )
        add_component(
            "SICK",
            sick_pay,
            f"Xəstəlik vərəqəsi: {sick_days} gün",
            flags=DEFAULT_FLAGS["SICK"],
        )
        add_component("BONUS_KPI", kpi_bonus, "KPI/OKR nəticəsinə görə bonus")

        for item, component in _employee_components(db, employee.id, year, month):
            if component.component_type == "DEDUCTION":
                continue
            amount = D(item.amount) if item.amount is not None else q(
                base_gross * D(item.percent or 0) / Decimal("100")
            )
            add_component(
                component.code,
                amount,
                f"Fərdi əlavə: {component.name}",
                flags={
                    "taxable": component.is_taxable,
                    "dsmf": component.is_dsmf_base,
                    "its": component.is_its_base,
                    "unemployment": component.is_unemployment_base,
                },
            )

        other_deductions = Decimal("0")
        deduction_details: list[dict] = []
        for item, component in _employee_components(db, employee.id, year, month):
            if component.component_type != "DEDUCTION":
                continue
            amount = D(item.amount) if item.amount is not None else q(
                gross_total * D(item.percent or 0) / Decimal("100")
            )
            amount = q(amount)
            if amount == 0:
                continue
            other_deductions += amount
            deduction_details.append(
                {
                    "component_code": component.code,
                    "direction": "DEDUCTION",
                    "amount": amount,
                    "base_amount": gross_total,
                    "quantity": None,
                    "rate": item.percent,
                    "calc_formula_note": f"Tutulma: {component.name}",
                }
            )

        exemptions = _exemption_total(db, employee.id, year, month)
        taxes = calculate_taxes(
            taxable_base=taxable_base,
            dsmf_base=dsmf_base,
            its_base=its_base,
            unemployment_base=unemployment_base,
            exemptions=exemptions,
            rules=rules,
        )

        net = q(
            gross_total
            - taxes["income_tax"]
            - taxes["dsmf_employee"]
            - taxes["its_employee"]
            - taxes["unemployment_employee"]
            - other_deductions
        )

        payroll_item = PayrollItem(
            payroll_run_id=run.id,
            employee_id=employee.id,
            contract_id=contract.id,
            timesheet_id=timesheet.id,
            worked_days=timesheet.worked_days,
            vacation_days=timesheet.vacation_days,
            sick_days=timesheet.sick_days,
            overtime_hours=D(timesheet.overtime_hours),
            gross_total=q(gross_total),
            taxable_base=taxes["taxable_base"],
            income_tax=taxes["income_tax"],
            dsmf_employee=taxes["dsmf_employee"],
            dsmf_employer=taxes["dsmf_employer"],
            its_employee=taxes["its_employee"],
            its_employer=taxes["its_employer"],
            unemployment_emp=taxes["unemployment_employee"],
            unemployment_org=taxes["unemployment_employer"],
            other_deductions=q(other_deductions),
            net_payable=net,
        )
        db.add(payroll_item)
        db.flush()

        for detail in details + deduction_details:
            db.add(PayrollItemDetail(payroll_item_id=payroll_item.id, **detail))

        totals["gross"] += gross_total
        totals["net"] += net
        totals["income_tax"] += taxes["income_tax"]
        totals["dsmf"] += taxes["dsmf_employee"] + taxes["dsmf_employer"]
        totals["its"] += taxes["its_employee"] + taxes["its_employer"]
        totals["unemployment"] += taxes["unemployment_employee"] + taxes["unemployment_employer"]

    for evaluation in synced_evaluations:
        evaluation.is_synced_to_payroll = True

    run.total_gross = q(totals["gross"])
    run.total_net = q(totals["net"])
    run.total_income_tax = q(totals["income_tax"])
    run.total_dsmf = q(totals["dsmf"])
    run.total_its = q(totals["its"])
    run.total_unemployment = q(totals["unemployment"])
    run.status = "CALCULATED"
    db.commit()
    db.refresh(run)
    return run


def approve_payroll_run(db: Session, run: PayrollRun, actor_id: int) -> PayrollRun:
    if run.status != "CALCULATED":
        raise ValueError("Yalnız CALCULATED statusunda olan hesablama təsdiqlənə bilər")
    run.status = "APPROVED"
    run.approved_by = actor_id
    run.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run


def pay_payroll_run(db: Session, run: PayrollRun) -> PayrollRun:
    if run.status != "APPROVED":
        raise ValueError("Yalnız APPROVED statusunda olan hesablama ödənilmiş kimi qeyd edilə bilər")
    run.status = "PAID"
    run.paid_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run
