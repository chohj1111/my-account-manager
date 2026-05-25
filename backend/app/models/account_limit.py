import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class AccountLimit(Base):
    __tablename__ = "account_limits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    tax_year: Mapped[int] = mapped_column(Integer)
    annual_limit: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # NULL = 무제한
    tax_deduction_limit: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # 연금저축 세액공제 한도
    benefit_type: Mapped[str] = mapped_column(String(50))  # TAX_FREE, TAX_DEDUCTION, NONE

    account: Mapped["Account"] = relationship(back_populates="account_limits")  # noqa: F821
