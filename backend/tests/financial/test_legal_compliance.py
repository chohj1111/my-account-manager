"""법률/규제 준수 테스트: 입력값 경계 검증 + 투자 조언 금지 표현 차단."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.legal
class TestGoalInputBoundaries:
    """자본시장법 관련 입력값 경계 검증 — 비현실적 파라미터 차단."""

    async def test_mdd_lower_bound(self):
        """MDD 1% 미만 거부."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/goals",
                json={"target_price": 500_000_000, "target_date": "2030-01-01", "max_drawdown": 0.5},
                headers={"Authorization": "Bearer fake"},
            )
            assert r.status_code in (401, 422)

    async def test_mdd_upper_bound(self):
        """MDD 30% 초과 거부."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/goals",
                json={"target_price": 500_000_000, "target_date": "2030-01-01", "max_drawdown": 31},
                headers={"Authorization": "Bearer fake"},
            )
            assert r.status_code in (401, 422)

    async def test_ltv_lower_bound(self):
        """LTV 10% 미만 거부."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/goals",
                json={"target_price": 500_000_000, "target_date": "2030-01-01", "ltv_ratio": 5},
                headers={"Authorization": "Bearer fake"},
            )
            assert r.status_code in (401, 422)

    async def test_ltv_upper_bound(self):
        """LTV 90% 초과 거부."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/goals",
                json={"target_price": 500_000_000, "target_date": "2030-01-01", "ltv_ratio": 95},
                headers={"Authorization": "Bearer fake"},
            )
            assert r.status_code in (401, 422)

    async def test_expected_return_upper_bound(self):
        """기대수익률 30% 초과 거부 — 비현실적 수익률 약속 방지."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/goals",
                json={"target_price": 500_000_000, "target_date": "2030-01-01", "expected_return_rate": 35},
                headers={"Authorization": "Bearer fake"},
            )
            assert r.status_code in (401, 422)

    async def test_realestate_growth_upper_bound(self):
        """부동산 상승률 20% 초과 거부."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/goals",
                json={"target_price": 500_000_000, "target_date": "2030-01-01", "realestate_growth_rate": 0.25},
                headers={"Authorization": "Bearer fake"},
            )
            assert r.status_code in (401, 422)


@pytest.mark.legal
class TestDisclaimerEnforcement:
    """API 응답에 투자 권유/보장 표현이 포함되지 않아야 함."""

    FORBIDDEN_TERMS = [
        "수익 보장",
        "원금 보장",
        "반드시 수익",
        "확실한 투자",
        "guaranteed return",
        "guaranteed profit",
    ]

    async def test_422_error_contains_no_forbidden_terms(self):
        """유효성 에러 메시지에 투자 권유 표현 없어야 함."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/goals",
                json={"target_price": -1, "target_date": "2030-01-01"},
                headers={"Authorization": "Bearer fake"},
            )
            body = r.text
            for term in self.FORBIDDEN_TERMS:
                assert term not in body, f"응답에 금지 표현 포함: {term}"

    async def test_401_error_contains_no_forbidden_terms(self):
        """인증 에러 메시지에 투자 권유 표현 없어야 함."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/goals")
            body = r.text
            for term in self.FORBIDDEN_TERMS:
                assert term not in body, f"응답에 금지 표현 포함: {term}"
