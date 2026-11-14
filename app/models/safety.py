from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SafetyBriefing(Base, TimestampMixin):
    __tablename__ = "safety_briefings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    briefing_type: Mapped[str] = mapped_column(String(30), nullable=False)
    briefing_date: Mapped[date] = mapped_column(Date, nullable=False)
    instructor: Mapped[str | None] = mapped_column(String(255))
    topic: Mapped[str | None] = mapped_column(String(255))
    signature_ref: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)


class MedicalExam(Base, TimestampMixin):
    __tablename__ = "medical_exams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_exam_date: Mapped[date | None] = mapped_column(Date, index=True)
    clinic: Mapped[str | None] = mapped_column(String(255))
    result: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)


class PpeIssuance(Base, TimestampMixin):
    __tablename__ = "ppe_issuances"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[str | None] = mapped_column(String(30))
    quantity: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=1, nullable=False)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    useful_life_months: Mapped[int | None] = mapped_column(Integer)
    return_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)


class SafetyIncident(Base, TimestampMixin):
    __tablename__ = "safety_incidents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="SET NULL")
    )
    incident_date: Mapped[date] = mapped_column(Date, nullable=False)
    incident_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str | None] = mapped_column(String(30))
    lost_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    investigation_status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False)
