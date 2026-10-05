from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.users import UserCreate


class EmailAlreadyRegisteredError(Exception):
    """Indica que el correo ya pertenece a una cuenta."""


async def register_user(session: AsyncSession, user_data: UserCreate) -> User:
    """Crea una cuenta nueva y guarda únicamente el hash de su contraseña."""
    user = User(
        email=user_data.email.casefold(),
        name=user_data.name,
        hashed_password=hash_password(user_data.password),
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise EmailAlreadyRegisteredError from exc

    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> User | None:
    """Devuelve la cuenta si el correo y la contraseña son válidos."""
    result = await session.scalar(
        select(User).where(User.email == email.casefold())
    )
    if result is None or not verify_password(password, result.hashed_password):
        return None
    return result


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Busca una cuenta por su identificador."""
    return await session.get(User, user_id)