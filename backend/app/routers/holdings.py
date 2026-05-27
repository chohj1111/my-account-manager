import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.account import Account
from app.models.goal import Goal
from app.models.holding import AssetClass, Holding
from app.models.schemas import HoldingCreate, HoldingResponse, HoldingUpdate
from app.models.user import User

router = APIRouter()


async def _get_user_holding(holding_id: uuid.UUID, user: User, db: AsyncSession) -> Holding:
    result = await db.execute(
        select(Holding)
        .join(Account, Holding.account_id == Account.id)
        .join(Goal, Account.goal_id == Goal.id)
        .where(Holding.id == holding_id, Goal.user_id == user.id)
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="보유 자산을 찾을 수 없습니다")
    return holding


@router.post("/{account_id}/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def create_holding(
    account_id: uuid.UUID,
    body: HoldingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # account가 해당 user 소유인지 확인
    result = await db.execute(
        select(Account).join(Goal, Account.goal_id == Goal.id).where(Account.id == account_id, Goal.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="계좌를 찾을 수 없습니다")

    try:
        asset_class = AssetClass(body.asset_class)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="유효하지 않은 자산 유형입니다")

    holding = Holding(
        account_id=account_id,
        ticker_name=body.ticker_name,
        asset_class=asset_class,
        quantity=body.quantity,
        current_price=body.current_price,
    )
    db.add(holding)
    await db.commit()
    await db.refresh(holding)
    return holding


@router.get("/{account_id}/holdings", response_model=list[HoldingResponse])
async def list_holdings(
    account_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Account).join(Goal, Account.goal_id == Goal.id).where(Account.id == account_id, Goal.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="계좌를 찾을 수 없습니다")

    result = await db.execute(select(Holding).where(Holding.account_id == account_id))
    return result.scalars().all()


@router.put("/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: uuid.UUID,
    body: HoldingUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    holding = await _get_user_holding(holding_id, user, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(holding, field, value)
    await db.commit()
    await db.refresh(holding)
    return holding


@router.delete("/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holding(
    holding_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    holding = await _get_user_holding(holding_id, user, db)
    await db.delete(holding)
    await db.commit()
