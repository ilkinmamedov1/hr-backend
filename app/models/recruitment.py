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
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Vacancy(Base, TimestampMixin):
    __tablename__ = "vacancies"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    staffing_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("staffing_table.id", ondelete="SET NULL")
    )
    department_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("departments.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    openings: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    requirements: Mapped[str | None] = mapped_column(Text)
    salary_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False, index=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))
    closed_at: Mapped[date | None] = mapped_column(Date)


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    cv_url: Mapped[str | None] = mapped_column(Text)
    skills_json: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb"), nullable=False
    )
    experience_years: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    current_position: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)


class Application(Base, TimestampMixin):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("vacancy_id", "candidate_id", name="uq_application_vacancy_candidate"),
    )
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vacancy_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage: Mapped[str] = mapped_column(String(30), default="NEW", nullable=False, index=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    applied_at: Mapped[date | None] = mapped_column(Date)
    hired_employee_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="SET NULL")
    )


class OnboardingTask(Base, TimestampMixin):
    __tablename__ = "onboarding_tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(30), default="HR", nullable=False)
    assignee: Mapped[str | None] = mapped_column(String(255))
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class OffboardingClearance(Base, TimestampMixin):
    __tablename__ = "offboarding_clearances"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    item: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
