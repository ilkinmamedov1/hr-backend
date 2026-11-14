from decimal import Decimal, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")
AVG_DAYS_IN_MONTH = Decimal("30.4")


def D(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def q(value: Any) -> Decimal:
    return D(value).quantize(CENT, rounding=ROUND_HALF_UP)


def bracket_total(amount: Any, brackets: list[dict]) -> Decimal:
    """Progressive (per-slice) bracket calculation.

    Example (DSMF employee): 3% up to 200, 10% above 200
    -> 200 * 3% + (amount - 200) * 10%.
    """
    amount = D(amount)
    if amount <= 0:
        return Decimal("0")

    ordered = sorted(
        brackets,
        key=lambda b: (b.get("up_to") is None, D(b.get("up_to") or 0)),
    )
    total = Decimal("0")
    lower = Decimal("0")
    for bracket in ordered:
        rate = D(bracket.get("rate", 0))
        upper = bracket.get("up_to")
        if upper is None:
            total += max(amount - lower, Decimal("0")) * rate
            break
        upper = D(upper)
        if amount > lower:
            total += (min(amount, upper) - lower) * rate
        lower = upper
    return total


def calculate_taxes(
    *,
    taxable_base: Any,
    dsmf_base: Any,
    its_base: Any,
    unemployment_base: Any,
    exemptions: Any,
    rules: dict,
) -> dict[str, Decimal]:
    taxable = max(D(taxable_base) - D(exemptions), Decimal("0"))
    income_tax = q(bracket_total(taxable, rules["income_tax"]["brackets"]))
    dsmf_employee = q(bracket_total(dsmf_base, rules["dsmf_employee"]["brackets"]))
    dsmf_employer = q(bracket_total(dsmf_base, rules["dsmf_employer"]["brackets"]))
    its_employee = q(bracket_total(its_base, rules["its_employee"]["brackets"]))
    its_employer = q(bracket_total(its_base, rules["its_employer"]["brackets"]))
    unemployment_employee = q(
        D(unemployment_base) * D(rules.get("unemployment_employee", {}).get("flat_rate", 0.005))
    )
    unemployment_employer = q(
        D(unemployment_base) * D(rules.get("unemployment_employer", {}).get("flat_rate", 0.005))
    )
    return {
        "income_tax": income_tax,
        "dsmf_employee": dsmf_employee,
        "dsmf_employer": dsmf_employer,
        "its_employee": its_employee,
        "its_employer": its_employer,
        "unemployment_employee": unemployment_employee,
        "unemployment_employer": unemployment_employer,
        "taxable_base": q(taxable),
    }


def average_daily_wage(months_total: Any, months_count: int) -> Decimal:
    if months_count <= 0:
        return Decimal("0")
    monthly = D(months_total) / Decimal(months_count)
    return monthly / AVG_DAYS_IN_MONTH


def sick_leave_coverage_pct(insurance_tenure_years: Any) -> int:
    years = float(D(insurance_tenure_years))
    if years < 8:
        return 60
    if years < 12:
        return 80
    return 100


def calculate_sick_leave_amounts(
    *,
    total_days: int,
    average_monthly_wage: Any,
    coverage_pct: int,
) -> dict[str, Any]:
    daily = D(average_monthly_wage) / AVG_DAYS_IN_MONTH
    employer_days = min(total_days, 14)
    dsmf_days = max(total_days - 14, 0)
    pct = D(coverage_pct) / Decimal("100")
    employer_amount = q(daily * Decimal(employer_days) * pct)
    dsmf_amount = q(daily * Decimal(dsmf_days) * pct)
    return {
        "average_daily_wage": q(daily),
        "employer_paid_days": employer_days,
        "dsmf_paid_days": dsmf_days,
        "employer_amount": employer_amount,
        "dsmf_amount": dsmf_amount,
        "calculated_amount": employer_amount + dsmf_amount,
    }
