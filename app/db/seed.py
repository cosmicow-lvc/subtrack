from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.charge import Charge
from app.models.sub import Sub
from app.models.user import User

DEMO_EMAIL = "demo@subtrack.local"
DEMO_PASSWORD = "Demo1234!"


def _billing_date_from_now() -> date:
	today = date.today()
	total_months = today.year * 12 + today.month - 1
	if today.day >= 5:
		total_months += 1
	year, month = divmod(total_months, 12)
	month += 1
	return date(year, month, min(5, monthrange(year, month)[1]))


def _previous_month(day: date, months_ago: int) -> date:
	total_months = day.year * 12 + day.month - 1 - months_ago
	year, month = divmod(total_months, 12)
	month += 1
	return date(year, month, min(5, monthrange(year, month)[1]))


async def seed_demo_data(session: AsyncSession) -> None:
	"""Crea una cuenta y actividad de ejemplo si aún no existen."""
	existing_user_id = await session.scalar(
		select(User.id).where(User.email == DEMO_EMAIL)
	)
	if existing_user_id is not None:
		return

	user = User(
		email=DEMO_EMAIL,
		name="Usuario Demo",
		hashed_password=hash_password(DEMO_PASSWORD),
	)
	session.add(user)
	await session.flush()

	subscriptions = [
		Sub(
			user_id=user.id,
			name="Netflix",
			amount=Decimal("14000"),
			frequency="monthly",
			category="entretenimiento",
			billing_date=_billing_date_from_now(),
			is_variable=False,
		),
		Sub(
			user_id=user.id,
			name="Spotify Premium",
			amount=Decimal("2500"),
			frequency="monthly",
			category="entretenimiento",
			billing_date=_billing_date_from_now(),
			is_variable=False,
		),
		Sub(
			user_id=user.id,
			name="Internet hogar",
			amount=Decimal("40000"),
			frequency="monthly",
			category="servicios",
			billing_date=_billing_date_from_now(),
			is_variable=False,
		),
	]
	session.add_all(subscriptions)
	await session.flush()

	today = date.today()
	charges = [
		Charge(
			sub_id=subscription.id,
			amount=subscription.amount,
			charged_at=_previous_month(today, months_ago),
		)
		for subscription in subscriptions
		for months_ago in range(1, 4)
	]
	session.add_all(charges)
	await session.commit()