from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.main import app
from app.models.sub import Sub
from app.models.user import User
from app.services import subs as subs_service


def make_sub() -> Sub:
	now = datetime.now(timezone.utc)
	return Sub(
		id=12,
		user_id=7,
		name="Streaming",
		amount=Decimal("9.99"),
		frequency="monthly",
		category="entertainment",
		billing_date=date(2026, 10, 5),
		is_variable=False,
		is_active=True,
		created_at=now,
		updated_at=now,
	)


@pytest.fixture
def client():
	async def override_db_session():
		yield object()

	async def override_current_user():
		return User(id=7)

	app.dependency_overrides[get_db_session] = override_db_session
	app.dependency_overrides[get_current_user] = override_current_user
	with TestClient(app) as test_client:
		yield test_client
	app.dependency_overrides.clear()


def test_create_sub_returns_subscription_for_current_user(client, monkeypatch):
	async def create_stub(session, user_id, sub_data):
		assert user_id == 7
		assert sub_data.name == "Streaming"
		return make_sub()

	monkeypatch.setattr(subs_service, "create_sub", create_stub)
	response = client.post(
		"/api/subs",
		json={
			"name": "Streaming",
			"amount": "9.99",
			"frequency": "monthly",
			"category": "entertainment",
			"billing_date": "2026-10-05",
		},
	)

	assert response.status_code == 201
	assert response.json()["user_id"] == 7
	assert response.json()["amount"] == "9.99"


def test_list_subs_uses_pagination(client, monkeypatch):
	async def list_stub(session, user_id, limit, offset):
		assert (user_id, limit, offset) == (7, 10, 5)
		return [make_sub()]

	monkeypatch.setattr(subs_service, "list_subs", list_stub)
	response = client.get("/api/subs?limit=10&offset=5")

	assert response.status_code == 200
	assert len(response.json()) == 1


def test_read_sub_returns_404_when_not_found(client, monkeypatch):
	async def get_stub(session, user_id, sub_id):
		assert (user_id, sub_id) == (7, 999)
		return None

	monkeypatch.setattr(subs_service, "get_sub", get_stub)
	response = client.get("/api/subs/999")

	assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_sub_marks_inactive_without_deleting_charges(monkeypatch):
	sub = make_sub()

	class Session:
		deleted = False
		committed = False

		async def delete(self, instance):
			self.deleted = True

		async def commit(self):
			self.committed = True

	session = Session()

	async def get_sub_stub(session, user_id, sub_id):
		assert (user_id, sub_id) == (7, 12)
		return sub

	monkeypatch.setattr(subs_service, "get_sub", get_sub_stub)

	assert await subs_service.delete_sub(session, user_id=7, sub_id=12)
	assert sub.is_active is False
	assert session.deleted is False
	assert session.committed is True


def test_create_sub_rejects_invalid_amount(client):
	response = client.post(
		"/api/subs",
		json={
			"name": "Streaming",
			"amount": "0",
			"frequency": "monthly",
			"category": "entertainment",
			"billing_date": "2026-10-05",
		},
	)

	assert response.status_code == 422