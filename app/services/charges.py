from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charge import Charge
from app.models.sub import Sub
from app.schemas.charges import ChargeCreate


class SubscriptionNotFoundError(Exception):
    """La suscripción no existe o no pertenece al usuario."""


def _six_month_window_start(today: date) -> date:
    """Devuelve el primer día del mes, contando este y los cinco anteriores."""
    month_index = today.year * 12 + today.month - 1 - 5
    return date(month_index // 12, month_index % 12 + 1, 1)


async def create_charge(
    session: AsyncSession, user_id: int, charge_data: ChargeCreate
) -> Charge:
    """Crea un cargo si la suscripción pertenece al usuario."""
    subscription_id = await session.scalar(
        select(Sub.id).where(
            Sub.id == charge_data.sub_id,
            Sub.user_id == user_id,
            Sub.is_active.is_(True),
        )
    )
    if subscription_id is None:
        raise SubscriptionNotFoundError

    charge = Charge(
        sub_id=charge_data.sub_id,
        amount=charge_data.amount,
        charged_at=charge_data.charged_at,
    )
    session.add(charge)
    await session.commit()
    await session.refresh(charge)
    return charge


async def list_charges(
    session: AsyncSession, user_id: int, limit: int, offset: int
) -> list[Charge]:
    """Lista cargos de suscripciones del usuario, del más reciente al más antiguo."""
    today = date.today()
    result = await session.scalars(
        select(Charge)
        .join(Charge.subscription)
        .where(
            Sub.user_id == user_id,
            Charge.charged_at >= _six_month_window_start(today),
            Charge.charged_at <= today,
        )
        .order_by(Charge.charged_at.desc(), Charge.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.all())


async def get_charge(
    session: AsyncSession, user_id: int, charge_id: int
) -> Charge | None:
    """Obtiene un cargo únicamente si pertenece al usuario."""
    return await session.scalar(
        select(Charge)
        .join(Charge.subscription)
        .where(Charge.id == charge_id, Sub.user_id == user_id)
    )


async def delete_charge(
    session: AsyncSession, user_id: int, charge_id: int
) -> bool:
    """Elimina un cargo del usuario y devuelve si existía."""
    charge = await get_charge(session, user_id, charge_id)
    if charge is None:
        return False

    await session.delete(charge)
    await session.commit()
    return True