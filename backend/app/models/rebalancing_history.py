import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class RebalancingHistory(Base):
    __tablename__ = "rebalancing_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"))
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    new_investment: Mapped[int] = mapped_column(BigInteger, default=0)
    result_snapshot: Mapped[dict] = mapped_column(JSONB)

    goal: Mapped["Goal"] = relationship(back_populates="rebalancing_history")  # noqa: F821
