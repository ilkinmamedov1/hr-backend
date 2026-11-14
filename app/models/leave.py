from datetime import date, time
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Computed,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LeaveType(Base, TimestampMixin):
    __tablename__ = "leave_types"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    affects_balance: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_days_per_year: Mapped[int | None] = mapped_column(Integer)
    labor_code_ref: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)


class LeaveBalance(Base, TimestampMixin):
    __tablename__ = "leave_balances"
    __table_args__ = (
        UniqueConstraint(
            "employee_id", "contract_id", "work_year_start", name="uq_leave_balance_period"
        ),
    )
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contract_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employment_contracts.id", ondelete="CASCADE"), nullable=False
    )
    work_year_start: Mapped[date] = mapped_column(Date, nullable=False)
    work_year_end: Mapped[date] = mapped_column(Date, nullable=False)
    entitled_base_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=21, nullable=False)
    entitled_extra_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0, nullable=False)
    used_days: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0, nullable=False)
    remaining_days: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        Computed("entitled_base_days + entitled_extra_days - used_days", persisted=True),
    )


class LeaveRequest(Base, TimestampMixin):
    __tablename__ = "leave_requests"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    leave_type_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("leave_types.id", ondelete="RESTRICT"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    calendar_days: Mapped[int] = mapped_column(Integer, nullable=False)
    paid_days: Mapped[int] = mapped_column(Integer, nullable=False)
    excluded_holidays: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False, index=True)
    order_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("hr_orders.id", ondelete="SET NULL")
    )
    reason: Mapped[str | None] = mapped_column(Text)
    approved_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))
    approved_at: Mapped[date | None] = mapped_column(Date)


class ShortLeaveRequest(Base, TimestampMixin):
    __tablename__ = "short_leave_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    leave_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    approved_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))


class SickLeave(Base, TimestampMixin):
    __tablename__ = "sick_leaves"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bulletin_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    employer_paid_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dsmf_paid_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coverage_pct: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    average_daily_wage: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    employer_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    dsmf_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    calculated_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
