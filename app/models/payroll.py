from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TaxSocialRateHistory(Base, TimestampMixin):
    __tablename__ = "tax_social_rates_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sector_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[date | None] = mapped_column(Date)
    rules_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)


class PayrollComponent(Base, TimestampMixin):
    __tablename__ = "payroll_components"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    component_type: Mapped[str] = mapped_column(String(20), default="EARNING", nullable=False)
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_dsmf_base: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_its_base: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_unemployment_base: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_in_vacation_avg: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_in_sick_avg: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)


class EmployeePayComponent(Base, TimestampMixin):
    __tablename__ = "employee_pay_components"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    component_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("payroll_components.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    percent: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)


class PayrollRun(Base, TimestampMixin):
    __tablename__ = "payroll_runs"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "period_year",
            "period_month",
            "run_type",
            name="uq_payroll_run_period",
        ),
    )
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    run_type: Mapped[str] = mapped_column(String(20), default="REGULAR", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    total_gross: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_net: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_income_tax: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_dsmf: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_its: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_unemployment: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    approved_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)


class PayrollItem(Base, TimestampMixin):
    __tablename__ = "payroll_items"
    __table_args__ = (
        UniqueConstraint("payroll_run_id", "employee_id", name="uq_payroll_item_run_employee"),
    )
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    payroll_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contract_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employment_contracts.id", ondelete="CASCADE"), nullable=False
    )
    timesheet_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("timesheets.id", ondelete="SET NULL")
    )
    worked_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vacation_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sick_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    gross_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    taxable_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    income_tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    dsmf_employee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    dsmf_employer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    its_employee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    its_employer: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    unemployment_emp: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    unemployment_org: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    other_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    net_payable: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)


class PayrollItemDetail(Base, TimestampMixin):
    __tablename__ = "payroll_item_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    payroll_item_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("payroll_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    component_code: Mapped[str] = mapped_column(String(30), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), default="EARNING", nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    base_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    calc_formula_note: Mapped[str | None] = mapped_column(Text)
