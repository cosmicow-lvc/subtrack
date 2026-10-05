from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sub import Sub
from app.schemas.subs import SubCreate


async def create_sub(
	session: AsyncSession, user_id: int, sub_data: SubCreate
) -> Sub:
	sub = Sub(user_id=user_id, **sub_data.model_dump())
	session.add(sub)
	await session.commit()
	await session.refresh(sub)
	return sub


async def list_subs(
	session: AsyncSession, user_id: int, limit: int, offset: int
) -> list[Sub]:
	result = await session.scalars(
		select(Sub)
		.where(Sub.user_id == user_id, Sub.is_active.is_(True))
		.order_by(Sub.billing_date, Sub.id)
		.limit(limit)
		.offset(offset)
	)
	return list(result.all())


async def get_sub(
	session: AsyncSession, user_id: int, sub_id: int
) -> Sub | None:
	return await session.scalar(
		select(Sub).where(Sub.id == sub_id, Sub.user_id == user_id)
	)


async def update_sub(
	session: AsyncSession, user_id: int, sub_id: int, sub_data: SubCreate
) -> Sub | None:
	sub = await get_sub(session, user_id, sub_id)
	if sub is None:
		return None

	for field, value in sub_data.model_dump().items():
		setattr(sub, field, value)
	await session.commit()
	await session.refresh(sub)
	return sub


async def delete_sub(
	session: AsyncSession, user_id: int, sub_id: int
) -> bool:
	sub = await get_sub(session, user_id, sub_id)
	if sub is None:
		return False

	if not sub.is_active:
		return False

	sub.is_active = False
	await session.commit()
	return True