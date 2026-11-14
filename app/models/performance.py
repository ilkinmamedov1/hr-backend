from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class KpiEvaluation(Base, TimestampMixin):
    __tablename__ = "kpi_evaluations"
    __audited__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    kpi_items_json: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb"), nullable=False
    )
    final_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    bonus_multiplier: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=1, nullable=False)
    is_synced_to_payroll: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    evaluated_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))
    notes: Mapped[str | None] = mapped_column(String(500))
