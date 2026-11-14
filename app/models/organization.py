from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(100))
    voen: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    sun_code: Mapped[str | None] = mapped_column(String(20))
    legal_address: Mapped[str | None] = mapped_column(Text)
    actual_address: Mapped[str | None] = mapped_column(Text)
    bank_name: Mapped[str | None] = mapped_column(String(255))
    bank_iban: Mapped[str | None] = mapped_column(String(34))
    bank_swift: Mapped[str | None] = mapped_column(String(20))
    director_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    sector_type: Mapped[str] = mapped_column(
        String(30), default="NON_OIL_PRIVATE", nullable=False
    )
    settings_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Department(Base, TimestampMixin):
    __tablename__ = "departments"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cost_center_code: Mapped[str | None] = mapped_column(String(50))
    head_employee_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    path: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Position(Base, TimestampMixin):
    __tablename__ = "positions"
    __table_args__ = (CheckConstraint("max_salary >= min_salary", name="ck_position_salary"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    occupation_code: Mapped[str | None] = mapped_column(String(30))
    grade_level: Mapped[int | None] = mapped_column(Integer)
    min_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    max_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    annual_leave_days: Mapped[int] = mapped_column(Integer, default=21, nullable=False)


class StaffingTable(Base, TimestampMixin):
    __tablename__ = "staffing_table"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("positions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    approved_headcount: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=1, nullable=False)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    harmful_work_bonus_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
