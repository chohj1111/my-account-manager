import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class AnnualDeposit(TimestampMixin, Base):
    __tablename__ = "annual_deposits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    tax_year: Mapped[int] = mapped_column(Integer)
    deposited_amount: Mapped[int] = mapped_column(BigInteger, default=0)

    account: Mapped["Account"] = relationship(back_populates="annual_deposits")  # noqa: F821
