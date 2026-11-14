from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
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


class EmasSyncLog(Base, TimestampMixin):
    __tablename__ = "emas_sync_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    request_payload: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
    response_payload: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
    emas_status: Mapped[str] = mapped_column(String(30), default="QUEUED", nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class GovernmentReport(Base, TimestampMixin):
    __tablename__ = "government_reports"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "report_type", "period_year", "period_month", "period_quarter",
            name="uq_government_report_period",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_month: Mapped[int | None] = mapped_column(Integer)
    period_quarter: Mapped[int | None] = mapped_column(Integer)
    headcount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fund_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    payload_json: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="GENERATED", nullable=False)
