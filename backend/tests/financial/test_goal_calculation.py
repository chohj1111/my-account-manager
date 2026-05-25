"""금융 계산 정확성 테스트: LTV, 월 투자액, 달성 가능성 판정."""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.deps import get_current_user
from app.main import app
from app.models.goal import Goal
from app.models.user import User


def _make_goal(**overrides) -> Goal:
    defaults = dict(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        target_price=500_000_000,
        target_date=date.today() + timedelta(days=5 * 365),
        max_drawdown=Decimal("5.00"),
        ltv_ratio=Decimal("60.00"),
        expected_return_rate=Decimal("5.00"),
        realestate_growth_rate=Decimal("0.0300"),
        current_total_asset=50_000_000,
    )
    defaults.update(overrides)
    goal = Goal(**defaults)
    # ORM timestamp 필드 시뮬레이션
    from datetime import datetime

    goal.created_at = datetime.now()
    goal.updated_at = datetime.now()
    return goal


def _mock_db_returning_goal(goal: Goal):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = goal

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    async def override():
        yield mock_session

    return override


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    app.dependency_overrides.clear()


@pytest.mark.financial
class TestTargetEquityCalculation:
    """target_equity = real_target_price × ltv_ratio / 100."""

    async def test_real_target_price_includes_growth_rate(self):
        """부동산 상승률이 목표 가격에 반영되어야 함."""
        goal = _make_goal(
            target_price=500_000_000,
            realestate_growth_rate=Decimal("0.0300"),
            ltv_ratio=Decimal("100.00"),  # LTV 100%로 설정하여 target_equity = real_target_price
        )
        user = User(id=goal.user_id, email="t@t.com", password_hash="x")

        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = _mock_db_returning_goal(goal)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get(f"/api/v1/goals/{goal.id}/summary")

        data = r.json()
        # 5년 3% 복리: 500_000_000 × (1.03)^5 ≈ 579_637_066
        assert data["target_equity"] > 500_000_000
        assert data["target_equity"] < 600_000_000

    async def test_ltv_ratio_applied_to_target_equity(self):
        """LTV 비율이 target_equity에 정확히 반영."""
        goal = _make_goal(
            target_price=500_000_000,
            realestate_growth_rate=Decimal("0.0000"),  # 성장률 0으로 고정
            ltv_ratio=Decimal("60.00"),
        )
        user = User(id=goal.user_id, email="t@t.com", password_hash="x")

        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = _mock_db_returning_goal(goal)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get(f"/api/v1/goals/{goal.id}/summary")

        data = r.json()
        # 성장률 0이므로 target_equity = 500_000_000 × 0.6 = 300_000_000
        assert data["target_equity"] == 300_000_000


@pytest.mark.financial
class TestMonthlyInvestmentCalculation:
    """월 적립액 산출 공식 검증."""

    async def test_zero_return_rate_uses_simple_division(self):
        """기대수익률 0%일 때 단순 나누기."""
        goal = _make_goal(
            target_price=300_000_000,
            realestate_growth_rate=Decimal("0.0000"),
            ltv_ratio=Decimal("100.00"),
            expected_return_rate=Decimal("0.00"),
            current_total_asset=0,
        )
        user = User(id=goal.user_id, email="t@t.com", password_hash="x")

        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = _mock_db_returning_goal(goal)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get(f"/api/v1/goals/{goal.id}/summary")

        data = r.json()
        months = data["d_day_months"]
        expected = 300_000_000 // months
        assert data["monthly_investment_needed"] == expected

    async def test_existing_assets_reduce_monthly_investment(self):
        """기존 자산이 있으면 월 투자액이 줄어야 함."""
        base = dict(
            target_price=300_000_000,
            realestate_growth_rate=Decimal("0.0000"),
            ltv_ratio=Decimal("100.00"),
            expected_return_rate=Decimal("5.00"),
        )
        goal_no_asset = _make_goal(current_total_asset=0, **base)
        goal_with_asset = _make_goal(current_total_asset=100_000_000, **base)
        user = User(id=goal_no_asset.user_id, email="t@t.com", password_hash="x")

        # 자산 0 케이스
        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = _mock_db_returning_goal(goal_no_asset)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r1 = await c.get(f"/api/v1/goals/{goal_no_asset.id}/summary")

        # 자산 1억 케이스
        goal_with_asset.user_id = user.id
        app.dependency_overrides[get_db] = _mock_db_returning_goal(goal_with_asset)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r2 = await c.get(f"/api/v1/goals/{goal_with_asset.id}/summary")

        assert r2.json()["monthly_investment_needed"] < r1.json()["monthly_investment_needed"]

    async def test_surplus_assets_yield_zero_monthly(self):
        """현재 자산이 목표를 초과하면 월 투자 0."""
        goal = _make_goal(
            target_price=100_000_000,
            realestate_growth_rate=Decimal("0.0000"),
            ltv_ratio=Decimal("100.00"),
            expected_return_rate=Decimal("5.00"),
            current_total_asset=200_000_000,
        )
        user = User(id=goal.user_id, email="t@t.com", password_hash="x")

        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = _mock_db_returning_goal(goal)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get(f"/api/v1/goals/{goal.id}/summary")

        assert r.json()["monthly_investment_needed"] == 0


@pytest.mark.financial
class TestAchievabilityThresholds:
    """달성 가능성 판정 기준 검증."""

    async def _get_achievability(self, monthly_needed_approx: int) -> str:
        """월 투자액이 특정 수준이 되도록 goal을 조정하여 achievability 반환."""
        # current_total_asset=0, return=0%로 고정하면 monthly = target / months
        # 5년 ≈ 60개월이므로 target = monthly_needed * 60
        target = monthly_needed_approx * 60
        goal = _make_goal(
            target_price=target,
            realestate_growth_rate=Decimal("0.0000"),
            ltv_ratio=Decimal("100.00"),
            expected_return_rate=Decimal("0.00"),
            current_total_asset=0,
        )
        user = User(id=goal.user_id, email="t@t.com", password_hash="x")

        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = _mock_db_returning_goal(goal)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get(f"/api/v1/goals/{goal.id}/summary")

        return r.json()["achievability"]

    async def test_achievable_under_5m(self):
        assert await self._get_achievability(3_000_000) == "ACHIEVABLE"

    async def test_risky_between_5m_and_10m(self):
        assert await self._get_achievability(7_000_000) == "RISKY"

    async def test_not_achievable_over_10m(self):
        assert await self._get_achievability(15_000_000) == "NOT_ACHIEVABLE"
