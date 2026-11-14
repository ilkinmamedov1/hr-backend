from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from app.services.calendar_service import FIXED_HOLIDAYS
from app.services.leave_service import add_years, work_year_period
from app.services.payroll_calculator import (
    average_daily_wage,
    bracket_total,
    calculate_sick_leave_amounts,
    calculate_taxes,
    sick_leave_coverage_pct,
)
from app.services.timesheet_service import TZ, _attendance_hours, _night_hours

NON_OIL_RULES = {
    "income_tax": {"brackets": [{"up_to": 8000, "rate": 0}, {"up_to": None, "rate": 0.14}]},
    "dsmf_employee": {"brackets": [{"up_to": 200, "rate": 0.03}, {"up_to": None, "rate": 0.10}]},
    "dsmf_employer": {"brackets": [{"up_to": 200, "rate": 0.22}, {"up_to": None, "rate": 0.15}]},
    "its_employee": {"brackets": [{"up_to": 8000, "rate": 0.02}, {"up_to": None, "rate": 0.005}]},
    "its_employer": {"brackets": [{"up_to": 8000, "rate": 0.02}, {"up_to": None, "rate": 0.005}]},
    "unemployment_employee": {"flat_rate": 0.005},
    "unemployment_employer": {"flat_rate": 0.005},
}

OIL_RULES = {
    **NON_OIL_RULES,
    "income_tax": {"brackets": [{"up_to": 2500, "rate": 0.14}, {"up_to": None, "rate": 0.25}]},
}


def test_bracket_total_progressive():
    brackets = [{"up_to": 200, "rate": 0.03}, {"up_to": None, "rate": 0.10}]
    assert bracket_total(200, brackets) == Decimal("6")
    assert bracket_total(1000, brackets) == Decimal("86")
    assert bracket_total(0, brackets) == Decimal("0")


def test_non_oil_private_taxes_below_and_above_8000():
    low = calculate_taxes(
        taxable_base=5000,
        dsmf_base=5000,
        its_base=5000,
        unemployment_base=5000,
        exemptions=0,
        rules=NON_OIL_RULES,
    )
    assert low["income_tax"] == Decimal("0.00")
    assert low["dsmf_employee"] == Decimal("486.00")
    assert low["dsmf_employer"] == Decimal("764.00")
    assert low["its_employee"] == Decimal("100.00")
    assert low["its_employer"] == Decimal("100.00")
    assert low["unemployment_employee"] == Decimal("25.00")

    high = calculate_taxes(
        taxable_base=10000,
        dsmf_base=10000,
        its_base=10000,
        unemployment_base=10000,
        exemptions=0,
        rules=NON_OIL_RULES,
    )
    assert high["income_tax"] == Decimal("280.00")
    assert high["dsmf_employee"] == Decimal("986.00")
    assert high["dsmf_employer"] == Decimal("1514.00")
    assert high["its_employee"] == Decimal("170.00")
    assert high["unemployment_employee"] == Decimal("50.00")


def test_oil_public_income_tax_brackets():
    result = calculate_taxes(
        taxable_base=3000,
        dsmf_base=3000,
        its_base=3000,
        unemployment_base=3000,
        exemptions=0,
        rules=OIL_RULES,
    )
    assert result["income_tax"] == Decimal("475.00")


def test_exemption_reduces_income_tax_base_only():
    result = calculate_taxes(
        taxable_base=3000,
        dsmf_base=3000,
        its_base=3000,
        unemployment_base=3000,
        exemptions=500,
        rules=NON_OIL_RULES,
    )
    assert result["taxable_base"] == Decimal("2500.00")
    assert result["income_tax"] == Decimal("0.00")
    assert result["dsmf_employee"] == Decimal("286.00")


def test_sick_leave_coverage_thresholds():
    assert sick_leave_coverage_pct(7.99) == 60
    assert sick_leave_coverage_pct(8) == 80
    assert sick_leave_coverage_pct(11.99) == 80
    assert sick_leave_coverage_pct(12) == 100


def test_sick_leave_split_14_days_employer_rest_dsmf():
    result = calculate_sick_leave_amounts(
        total_days=20,
        average_monthly_wage=average_daily_wage(6080, 2) * Decimal("30.4"),
        coverage_pct=80,
    )
    assert average_daily_wage(6080, 2) == Decimal("100")
    assert result["employer_paid_days"] == 14
    assert result["dsmf_paid_days"] == 6
    assert result["employer_amount"] == Decimal("1120.00")
    assert result["dsmf_amount"] == Decimal("480.00")
    assert result["calculated_amount"] == Decimal("1600.00")


def test_average_daily_wage():
    assert average_daily_wage(3040, 1) == Decimal("100")
    assert average_daily_wage(0, 0) == Decimal("0")


def test_work_year_boundaries_and_leap_day():
    assert add_years(date(2024, 2, 29), 1) == date(2025, 2, 28)
    start, end = work_year_period(date(2024, 2, 29), date(2025, 2, 28))
    assert start == date(2025, 2, 28)
    assert end == date(2026, 2, 27)
    start, end = work_year_period(date(2024, 2, 29), date(2026, 3, 1))
    assert start == date(2026, 2, 28)
    assert end == date(2027, 2, 27)


def test_night_hours_window():
    start = datetime(2026, 11, 2, 20, 0, tzinfo=TZ)
    end = datetime(2026, 11, 3, 6, 0, tzinfo=TZ)
    assert _night_hours(start, end) == Decimal("8")
    assert _night_hours(
        datetime(2026, 11, 2, 21, 0, tzinfo=TZ),
        datetime(2026, 11, 2, 23, 0, tzinfo=TZ),
    ) == Decimal("1")


def test_attendance_hours_excludes_lunch_break():
    punches = [
        SimpleNamespace(punch_time=datetime(2026, 11, 2, 9, 0, tzinfo=TZ)),
        SimpleNamespace(punch_time=datetime(2026, 11, 2, 18, 0, tzinfo=TZ)),
    ]
    hours, night = _attendance_hours(punches, Decimal("1"))
    assert hours == Decimal("8")
    assert night == Decimal("0")

    long_day = [
        SimpleNamespace(punch_time=datetime(2026, 11, 2, 9, 0, tzinfo=TZ)),
        SimpleNamespace(punch_time=datetime(2026, 11, 2, 20, 0, tzinfo=TZ)),
    ]
    hours, _ = _attendance_hours(long_day, Decimal("1"))
    assert hours == Decimal("10")


def test_holiday_calendar_covers_current_year():
    assert 2026 in FIXED_HOLIDAYS
    assert (11, 8) in FIXED_HOLIDAYS[2026]
    assert (11, 9) in FIXED_HOLIDAYS[2026]
    assert ZoneInfo("Asia/Baku").key == "Asia/Baku"
