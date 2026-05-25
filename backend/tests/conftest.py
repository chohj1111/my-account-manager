import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.deps import get_current_user
from app.main import app
from app.models.user import User


def _make_fake_user(user_id: uuid.UUID | None = None) -> User:
    return User(
        id=user_id or uuid.uuid4(),
        email="test@example.com",
        password_hash="fake",
    )


@pytest.fixture
def fake_user():
    return _make_fake_user()


@pytest.fixture
def other_user():
    return _make_fake_user()


@pytest.fixture
def client_factory():
    """인증된 클라이언트를 생성하는 팩토리. DB 의존성을 mock으로 대체."""

    def _create(user: User, db_session=None):
        app.dependency_overrides[get_current_user] = lambda: user
        if db_session is not None:
            app.dependency_overrides[get_db] = lambda: db_session
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    return _create


@pytest.fixture(autouse=True)
def _cleanup_overrides():
    yield
    app.dependency_overrides.clear()
