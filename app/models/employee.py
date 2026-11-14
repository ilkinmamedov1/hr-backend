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
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"
    __table_args__ = (UniqueConstraint("organization_id", "pin_code", name="uq_employee_org_pin"),)
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pin_code: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    father_name: Mapped[str | None] = mapped_column(String(100))
    birth_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(1))
    citizenship: Mapped[str] = mapped_column(String(50), default="AZ", nullable=False)
    marital_status: Mapped[str | None] = mapped_column(String(30))
    ssn: Mapped[str | None] = mapped_column(String(20), index=True)
    individual_voen: Mapped[str | None] = mapped_column(String(10))
    id_card_number: Mapped[str | None] = mapped_column(String(30))
    id_card_issue_date: Mapped[date | None] = mapped_column(Date)
    id_card_expiry_date: Mapped[date | None] = mapped_column(Date)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    bank_name: Mapped[str | None] = mapped_column(String(255))
    bank_iban: Mapped[str | None] = mapped_column(String(34))
    photo_path: Mapped[str | None] = mapped_column(Text)
    total_insurance_tenure_years: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EmployeeDocument(Base, TimestampMixin):
    __tablename__ = "employee_documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doc_type: Mapped[str] = mapped_column(String(40), nullable=False)
    doc_number: Mapped[str | None] = mapped_column(String(50))
    issue_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date, index=True)
    file_path: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)


class EmployeeTaxExemption(Base, TimestampMixin):
    __tablename__ = "employee_tax_exemptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exemption_code: Mapped[str] = mapped_column(String(30), nullable=False)
    monthly_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    doc_reference: Mapped[str | None] = mapped_column(String(100))
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date)


class EmployeeFamilyMember(Base, TimestampMixin):
    __tablename__ = "employee_family_members"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relation: Mapped[str] = mapped_column(String(30), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date)
    is_dependent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    document_number: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)


class EmployeeEducation(Base, TimestampMixin):
    __tablename__ = "employee_education"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    degree_level: Mapped[str | None] = mapped_column(String(50))
    specialty: Mapped[str | None] = mapped_column(String(255))
    diploma_number: Mapped[str | None] = mapped_column(String(50))
    start_year: Mapped[int | None] = mapped_column(Integer)
    end_year: Mapped[int | None] = mapped_column(Integer)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class EmployeeMilitary(Base, TimestampMixin):
    __tablename__ = "employee_military"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    military_ticket_number: Mapped[str | None] = mapped_column(String(50))
    rank: Mapped[str | None] = mapped_column(String(100))
    specialty: Mapped[str | None] = mapped_column(String(255))
    registration_office: Mapped[str | None] = mapped_column(String(255))
    is_liable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class EmployeeMigration(Base, TimestampMixin):
    __tablename__ = "employee_migrations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    permit_type: Mapped[str] = mapped_column(String(30), nullable=False)
    permit_number: Mapped[str] = mapped_column(String(50), nullable=False)
    issue_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date, index=True)
    country: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
