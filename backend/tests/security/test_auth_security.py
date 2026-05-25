"""보안 테스트: 인증 우회, 토큰 위조, 타인 데이터 접근 차단."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.security
class TestAuthSecurity:
    """인증 우회 시도 차단 검증."""

    async def test_goals_reject_no_token(self):
        """토큰 없이 Goal API 접근 시 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/api/v1/goals")
            assert r.status_code in (401, 403)

    async def test_goals_reject_invalid_token(self):
        """위조 토큰으로 접근 시 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/api/v1/goals", headers={"Authorization": "Bearer forged.token.here"})
            assert r.status_code == 401

    async def test_goals_reject_expired_refresh_as_access(self):
        """refresh 토큰을 access 토큰으로 사용하면 거부."""
        from app.core.security import create_refresh_token

        refresh = create_refresh_token({"sub": "00000000-0000-0000-0000-000000000000"})
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/api/v1/goals", headers={"Authorization": f"Bearer {refresh}"})
            assert r.status_code == 401

    async def test_refresh_rejects_access_token(self):
        """access 토큰을 refresh 용도로 사용하면 거부."""
        from app.core.security import create_access_token

        access = create_access_token({"sub": "00000000-0000-0000-0000-000000000000"})
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/v1/auth/refresh", json={"refresh_token": access})
            assert r.status_code == 401
