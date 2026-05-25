import enum
import uuid
from decimal import Decimal

from sqlalchemy import BigInteger, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class AssetClass(str, enum.Enum):
    STOCK = "STOCK"
    BOND = "BOND"
    CASH = "CASH"


class Holding(TimestampMixin, Base):
    __tablename__ = "holdings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    ticker_name: Mapped[str] = mapped_column(String(100))
    asset_class: Mapped[AssetClass] = mapped_column(Enum(AssetClass))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    current_price: Mapped[int] = mapped_column(BigInteger)  # 원

    account: Mapped["Account"] = relationship(back_populates="holdings")  # noqa: F821
