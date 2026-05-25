import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Goal(TimestampMixin, Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    target_price: Mapped[int] = mapped_column(BigInteger)  # 목표 주택 가격 (원)
    target_date: Mapped[date] = mapped_column(Date)
    max_drawdown: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("5.00"))
    ltv_ratio: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("60.00"))
    expected_return_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("5.00"))
    realestate_growth_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.0300"))
    current_total_asset: Mapped[int] = mapped_column(BigInteger, default=0)

    user: Mapped["User"] = relationship(back_populates="goals")  # noqa: F821
    accounts: Mapped[list["Account"]] = relationship(back_populates="goal", cascade="all, delete-orphan")  # noqa: F821
    target_allocations: Mapped[list["TargetAllocation"]] = relationship(  # noqa: F821
        back_populates="goal",
        cascade="all, delete-orphan",
    )
    rebalancing_history: Mapped[list["RebalancingHistory"]] = relationship(  # noqa: F821
        back_populates="goal",
        cascade="all, delete-orphan",
    )
