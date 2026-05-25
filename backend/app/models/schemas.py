import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

# ─── Auth ───────────────────────────────────────────────


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# ─── Goal ───────────────────────────────────────────────


class GoalCreate(BaseModel):
    target_price: int = Field(gt=0, description="목표 주택 가격 (원)")
    target_date: date
    max_drawdown: Decimal = Field(default=Decimal("5.00"), ge=1, le=30)
    ltv_ratio: Decimal = Field(default=Decimal("60.00"), ge=10, le=90)
    expected_return_rate: Decimal = Field(default=Decimal("5.00"), ge=0, le=30)
    realestate_growth_rate: Decimal = Field(default=Decimal("0.0300"), ge=0, le=0.2)
    current_total_asset: int = Field(default=0, ge=0)


class GoalUpdate(BaseModel):
    target_price: int | None = Field(default=None, gt=0)
    target_date: date | None = None
    max_drawdown: Decimal | None = Field(default=None, ge=1, le=30)
    ltv_ratio: Decimal | None = Field(default=None, ge=10, le=90)
    expected_return_rate: Decimal | None = Field(default=None, ge=0, le=30)
    realestate_growth_rate: Decimal | None = Field(default=None, ge=0, le=0.2)
    current_total_asset: int | None = Field(default=None, ge=0)


class GoalResponse(BaseModel):
    id: uuid.UUID
    target_price: int
    target_date: date
    max_drawdown: Decimal
    ltv_ratio: Decimal
    expected_return_rate: Decimal
    realestate_growth_rate: Decimal
    current_total_asset: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GoalSummary(BaseModel):
    goal: GoalResponse
    d_day_months: int
    target_equity: int
    gap: int
    monthly_investment_needed: int
    achievability: str
