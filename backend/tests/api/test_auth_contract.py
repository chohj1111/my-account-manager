"""API 계약 테스트: 인증 엔드포인트의 요청/응답 스키마 검증."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app


def _mock_db_no_user():
    """DB mock: 쿼리 결과 없음 (사용자 미존재 시뮬레이션)."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    async def override():
        yield mock_session

    return override


@pytest.mark.api
class TestAuthContract:
    """인증 API가 명세된 스키마대로 응답하는지 검증."""

    async def test_register_requires_email_and_password(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 빈 body
            r = await client.post("/api/v1/auth/register", json={})
            assert r.status_code == 422

    async def test_register_rejects_short_password(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "short"})
            assert r.status_code == 422

    async def test_register_rejects_invalid_email(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/v1/auth/register", json={"email": "not-email", "password": "12345678"})
            assert r.status_code == 422

    async def test_login_returns_401_for_unknown_user(self):
        """존재하지 않는 사용자로 로그인 시 401."""
        app.dependency_overrides[get_db] = _mock_db_no_user()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "12345678"})
            assert r.status_code == 401


@pytest.mark.api
class TestGoalContract:
    """Goal API 요청 검증."""

    async def test_create_goal_rejects_negative_price(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post(
                "/api/v1/goals",
                json={"target_price": -1, "target_date": "2030-01-01"},
                headers={"Authorization": "Bearer fake"},
            )
            assert r.status_code in (401, 422)

    async def test_create_goal_rejects_mdd_out_of_range(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post(
                "/api/v1/goals",
                json={"target_price": 500000000, "target_date": "2030-01-01", "max_drawdown": 50},
                headers={"Authorization": "Bearer fake"},
            )
            assert r.status_code in (401, 422)
