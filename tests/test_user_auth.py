from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token, decode_access_token
from app.db.session import get_db_session
from app.main import app
from app.models.user import User
from app.schemas.users import UserCreate
from app.services import users as users_service


def make_user(email: str = "ana@example.com") -> User:
    now = datetime.now(timezone.utc)
    return User(
        id=7,
        email=email,
        name="Ana",
        hashed_password="hashed-password",
        role="user",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def client():
    async def override_db_session():
        yield object()

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_register_returns_user_without_password(client, monkeypatch):
    async def register_stub(session, user_data):
        return make_user(user_data.email)

    monkeypatch.setattr(users_service, "register_user", register_stub)

    response = client.post(
        "/api/users/register",
        json={
            "email": "ana@example.com",
            "name": "Ana",
            "password": "password-segura",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "ana@example.com"
    assert "hashed_password" not in response.json()
    assert "password" not in response.json()


def test_login_returns_bearer_token(client, monkeypatch):
    async def authenticate_stub(session, email, password):
        return make_user(email)

    monkeypatch.setattr(users_service, "authenticate_user", authenticate_stub)

    response = client.post(
        "/api/users/login",
        json={"email": "ana@example.com", "password": "password-segura"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert decode_access_token(response.json()["access_token"]) == 7


def test_current_user_requires_a_valid_bearer_token(client, monkeypatch):
    async def user_by_id_stub(session, user_id):
        return make_user()

    monkeypatch.setattr(users_service, "get_user_by_id", user_by_id_stub)

    unauthorized = client.get("/api/users/me")
    assert unauthorized.status_code == 401

    token = create_access_token(7)
    profile = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert profile.status_code == 200
    assert profile.json()["id"] == 7


@pytest.mark.asyncio
async def test_register_service_hashes_password_before_saving():
    session = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    user_data = UserCreate(
        email="ana@example.com",
        name="Ana",
        password="password-segura",
    )

    user = await users_service.register_user(session, user_data)

    session.add.assert_called_once_with(user)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)
    assert user.hashed_password != user_data.password