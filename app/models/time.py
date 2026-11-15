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
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ProductionCalendar(Base, TimestampMixin):
    __tablename__ = "production_calendar"

    cal_date: Mapped[date] = mapped_column(Date, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    day_type: Mapped[str] = mapped_column(String(20), nullable=False, default="WORKDAY")
    norm_hours_40: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=8, nullable=False)
    norm_hours_36: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=7.2, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))


class WorkSchedule(Base, TimestampMixin):
    __tablename__ = "work_schedules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(30), default="STANDARD_5", nullable=False)
    weekly_hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=40, nullable=False)
    shift_rules_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class EmployeeSchedule(Base, TimestampMixin):
    __tablename__ = "employee_schedules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_schedule_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("work_schedules.id", ondelete="CASCADE"), nullable=False
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date)


class AttendanceLog(Base, TimestampMixin):
    __tablename__ = "attendance_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    punch_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), default="IN", nullable=False)
    device_id: Mapped[str | None] = mapped_column(String(50))
    is_manual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )


class Timesheet(Base, TimestampMixin):
    __tablename__ = "timesheets"
    __table_args__ = (
        UniqueConstraint("contract_id", "year", "month", name="uq_timesheet_contract_period"),
    )
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contract_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employment_contracts.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    worked_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    planned_hours: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    regular_hours: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    night_hours: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    holiday_hours: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=0, nullable=False)
    vacation_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sick_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trip_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    absent_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    approved_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))
    daily_records_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
