from datetime import date
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
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EmploymentContract(Base, TimestampMixin):
    __tablename__ = "employment_contracts"
    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_contract_dates"),
        UniqueConstraint("organization_id", "contract_number", name="uq_contract_number"),
    )
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    staffing_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("staffing_table.id", ondelete="RESTRICT"), nullable=False
    )
    contract_number: Mapped[str] = mapped_column(String(50), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(30), default="INDEFINITE", nullable=False)
    work_type: Mapped[str] = mapped_column(String(20), default="MAIN", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    probation_end_date: Mapped[date | None] = mapped_column(Date)
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    salary_type: Mapped[str] = mapped_column(String(20), default="MONTHLY", nullable=False)
    annual_leave_days: Mapped[int | None] = mapped_column(Integer)
    signed_date: Mapped[date | None] = mapped_column(Date)
    termination_date: Mapped[date | None] = mapped_column(Date)
    termination_article: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text)


class ContractAmendment(Base, TimestampMixin):
    __tablename__ = "contract_amendments"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    contract_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employment_contracts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amendment_no: Mapped[str] = mapped_column(String(50), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    old_salary: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    new_salary: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    old_staffing_id: Mapped[int | None] = mapped_column(BigInteger)
    new_staffing_id: Mapped[int | None] = mapped_column(BigInteger)
    old_end_date: Mapped[date | None] = mapped_column(Date)
    new_end_date: Mapped[date | None] = mapped_column(Date)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)


class HrOrder(Base, TimestampMixin):
    __tablename__ = "hr_orders"
    __table_args__ = (
        UniqueConstraint("organization_id", "order_number", name="uq_hr_order_number"),
    )
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_number: Mapped[str] = mapped_column(String(50), nullable=False)
    order_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    labor_code_article: Mapped[str | None] = mapped_column(String(20))
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    payload_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))


class ServiceContract(Base, TimestampMixin):
    __tablename__ = "service_contracts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contractor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contractor_voen: Mapped[str | None] = mapped_column(String(10))
    contract_number: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    service_description: Mapped[str | None] = mapped_column(Text)
    withholding_tax_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=14, nullable=False)
    dsmf_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    payment_details: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
