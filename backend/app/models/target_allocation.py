import uuid
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid
from app.models.holding import AssetClass


class TargetAllocation(TimestampMixin, Base):
    __tablename__ = "target_allocations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"))
    asset_class: Mapped[AssetClass] = mapped_column(Enum(AssetClass))
    target_weight: Mapped[Decimal] = mapped_column(Numeric(5, 2))  # 합계 100.00

    goal: Mapped["Goal"] = relationship(back_populates="target_allocations")  # noqa: F821
