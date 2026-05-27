import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.account import Account, AccountType
from app.models.goal import Goal
from app.models.schemas import AccountCreate, AccountResponse, AccountUpdate
from app.models.user import User

router = APIRouter()


async def _get_user_account(account_id: uuid.UUID, user: User, db: AsyncSession) -> Account:
    result = await db.execute(
        select(Account).join(Goal, Account.goal_id == Goal.id).where(Account.id == account_id, Goal.user_id == user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="계좌를 찾을 수 없습니다")
    return account


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    body: AccountCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # goal이 해당 user 소유인지 확인
    goal = await db.execute(select(Goal).where(Goal.id == body.goal_id, Goal.user_id == user.id))
    if not goal.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="목표를 찾을 수 없습니다")

    try:
        account_type = AccountType(body.account_type)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="유효하지 않은 계좌 유형입니다")

    # ISA 계좌는 목표당 1개만 허용
    if account_type == AccountType.ISA:
        existing = await db.execute(
            select(Account).where(Account.goal_id == body.goal_id, Account.account_type == AccountType.ISA)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ISA 계좌는 목표당 1개만 등록 가능합니다")

    account = Account(
        goal_id=body.goal_id,
        account_type=account_type,
        account_name=body.account_name,
        is_emergency_fund=body.is_emergency_fund,
        isa_opened_at=body.isa_opened_at,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/goal/{goal_id}", response_model=list[AccountResponse])
async def list_accounts_by_goal(
    goal_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user.id))
    if not goal.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="목표를 찾을 수 없습니다")

    result = await db.execute(select(Account).where(Account.goal_id == goal_id))
    return result.scalars().all()


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: uuid.UUID,
    body: AccountUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await _get_user_account(account_id, user, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await _get_user_account(account_id, user, db)
    await db.delete(account)
    await db.commit()
