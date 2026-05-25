import enum
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class AccountType(str, enum.Enum):
    ISA = "ISA"
    PENSION = "PENSION"
    GENERAL = "GENERAL"


class Account(TimestampMixin, Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"))
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    account_name: Mapped[str] = mapped_column(String(100))
    is_emergency_fund: Mapped[bool] = mapped_column(Boolean, default=False)
    isa_opened_at: Mapped[date | None] = mapped_column(Date, nullable=True)  # ISA 전용

    goal: Mapped["Goal"] = relationship(back_populates="accounts")  # noqa: F821
    holdings: Mapped[list["Holding"]] = relationship(back_populates="account", cascade="all, delete-orphan")  # noqa: F821
    account_limits: Mapped[list["AccountLimit"]] = relationship(back_populates="account", cascade="all, delete-orphan")  # noqa: F821
    annual_deposits: Mapped[list["AnnualDeposit"]] = relationship(back_populates="account", cascade="all, delete-orphan")  # noqa: F821
