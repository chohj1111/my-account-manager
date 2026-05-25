import uuid
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.goal import Goal
from app.models.schemas import GoalCreate, GoalResponse, GoalSummary, GoalUpdate
from app.models.user import User

router = APIRouter()


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    body: GoalCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = Goal(user_id=user.id, **body.model_dump())
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


@router.get("", response_model=list[GoalResponse])
async def list_goals(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Goal).where(Goal.user_id == user.id))
    return result.scalars().all()


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await _get_user_goal(goal_id, user.id, db)
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: uuid.UUID,
    body: GoalUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await _get_user_goal(goal_id, user.id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    await db.commit()
    await db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await _get_user_goal(goal_id, user.id, db)
    await db.delete(goal)
    await db.commit()


@router.get("/{goal_id}/summary", response_model=GoalSummary)
async def get_goal_summary(
    goal_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await _get_user_goal(goal_id, user.id, db)

    today = date.today()
    years = (goal.target_date - today).days / Decimal("365.25")
    months = int(years * 12)

    real_target_price = int(goal.target_price * (1 + goal.realestate_growth_rate) ** years)
    target_equity = int(real_target_price * goal.ltv_ratio / 100)
    gap = target_equity - goal.current_total_asset

    monthly_rate = float(goal.expected_return_rate) / 100 / 12
    if monthly_rate == 0 or months <= 0:
        monthly_investment = gap // max(months, 1)
    else:
        fv_current = goal.current_total_asset * ((1 + monthly_rate) ** months)
        remaining_gap = target_equity - fv_current
        if remaining_gap <= 0:
            monthly_investment = 0
        else:
            monthly_investment = int(remaining_gap * monthly_rate / (((1 + monthly_rate) ** months) - 1))

    if monthly_investment < 5_000_000:
        achievability = "ACHIEVABLE"
    elif monthly_investment < 10_000_000:
        achievability = "RISKY"
    else:
        achievability = "NOT_ACHIEVABLE"

    return GoalSummary(
        goal=goal,
        d_day_months=months,
        target_equity=target_equity,
        gap=gap,
        monthly_investment_needed=monthly_investment,
        achievability=achievability,
    )


async def _get_user_goal(goal_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Goal:
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="목표를 찾을 수 없습니다")
    return goal
