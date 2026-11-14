from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Training(Base, TimestampMixin):
    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    training_type: Mapped[str] = mapped_column(String(30), default="INTERNAL", nullable=False)
    provider: Mapped[str | None] = mapped_column(String(255))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PLANNED", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class TrainingParticipant(Base, TimestampMixin):
    __tablename__ = "training_participants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    training_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("trainings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    certificate_number: Mapped[str | None] = mapped_column(String(100))
    certificate_expiry: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="REGISTERED", nullable=False)


class EmployeeCertificate(Base, TimestampMixin):
    __tablename__ = "employee_certificates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(255))
    number: Mapped[str | None] = mapped_column(String(100))
    issue_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date, index=True)
    file_path: Mapped[str | None] = mapped_column(Text)
