from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.users import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services import users as users_service


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
	"/register",
	response_model=UserResponse,
	status_code=status.HTTP_201_CREATED,
)
async def register_user(
	user_data: UserCreate,
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
	try:
		return await users_service.register_user(session, user_data)
	except users_service.EmailAlreadyRegisteredError as exc:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Ya existe una cuenta con ese correo",
		) from exc


@router.post("/login", response_model=TokenResponse)
async def login(
	credentials: UserLogin,
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
	user = await users_service.authenticate_user(
		session, credentials.email, credentials.password
	)
	if user is None or not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Correo o contraseña incorrectos",
			headers={"WWW-Authenticate": "Bearer"},
		)

	return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
async def read_current_user(
	current_user: Annotated[User, Depends(get_current_user)],
) -> User:
	return current_user
