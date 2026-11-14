from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class BusinessTrip(Base, TimestampMixin):
    __tablename__ = "business_trips"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_city: Mapped[str] = mapped_column(String(150), nullable=False)
    is_foreign: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text)
    daily_allowance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    hotel_limit: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_advance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    actual_expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    order_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("hr_orders.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class TripExpenseReport(Base, TimestampMixin):
    __tablename__ = "trip_expense_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    trip_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("business_trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    advance_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    items_json: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="SUBMITTED", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
