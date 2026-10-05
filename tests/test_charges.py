from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.main import app
from app.models.charge import Charge
from app.models.user import User
from app.services import charges as charges_service


def make_charge() -> Charge:
    now = datetime.now(timezone.utc)
    return Charge(
        id=12,
        sub_id=4,
        amount=Decimal("999"),
        charged_at=date(2026, 10, 5),
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


def test_create_charge_returns_charge_for_current_user(client, monkeypatch):
    async def create_stub(session, user_id, charge_data):
        assert user_id == 7
        assert charge_data.sub_id == 4
        return make_charge()

    monkeypatch.setattr(charges_service, "create_charge", create_stub)

    response = client.post(
        "/api/charges",
        json={"sub_id": 4, "amount": "9.99", "charged_at": "2026-10-05"},
    )

    assert response.status_code == 201
    assert response.json()["sub_id"] == 4
    assert response.json()["amount"] == "999"


def test_create_charge_returns_404_for_unowned_subscription(client, monkeypatch):
    async def create_stub(session, user_id, charge_data):
        raise charges_service.SubscriptionNotFoundError

    monkeypatch.setattr(charges_service, "create_charge", create_stub)

    response = client.post(
        "/api/charges",
        json={"sub_id": 999, "amount": "9.99", "charged_at": "2026-10-05"},
    )

    assert response.status_code == 404


def test_list_charges_uses_pagination(client, monkeypatch):
    async def list_stub(session, user_id, limit, offset):
        assert (user_id, limit, offset) == (7, 10, 5)
        return [make_charge()]

    monkeypatch.setattr(charges_service, "list_charges", list_stub)

    response = client.get("/api/charges?limit=10&offset=5")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_charges_filters_to_six_month_window(monkeypatch):
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 10, 5)

    class Result:
        def all(self):
            return []

    class Session:
        statement = None

        async def scalars(self, statement):
            self.statement = statement
            return Result()

    session = Session()
    monkeypatch.setattr(charges_service, "date", FrozenDate)

    await charges_service.list_charges(session, user_id=7, limit=50, offset=0)

    params = session.statement.compile().params.values()
    assert date(2026, 5, 1) in params
    assert date(2026, 10, 5) in params
    assert "subscriptions.is_active" not in str(session.statement.compile())


def test_create_charge_rejects_invalid_amount(client):
    response = client.post(
        "/api/charges",
        json={"sub_id": 4, "amount": "0", "charged_at": "2026-10-05"},
    )

    assert response.status_code == 422