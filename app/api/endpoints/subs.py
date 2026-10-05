from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.subs import SubCreate, SubResponse
from app.services import subs as subs_service


router = APIRouter(prefix="/subs", tags=["subs"])


@router.post("", response_model=SubResponse, status_code=status.HTTP_201_CREATED)
async def create_sub(
	sub_data: SubCreate,
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
) -> SubResponse:
	return await subs_service.create_sub(session, current_user.id, sub_data)


@router.get("", response_model=list[SubResponse])
async def list_subs(
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
	limit: Annotated[int, Query(ge=1, le=100)] = 50,
	offset: Annotated[int, Query(ge=0)] = 0,
) -> list[SubResponse]:
	return await subs_service.list_subs(
		session, current_user.id, limit, offset
	)


@router.get("/{sub_id}", response_model=SubResponse)
async def read_sub(
	sub_id: int,
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
) -> SubResponse:
	sub = await subs_service.get_sub(session, current_user.id, sub_id)
	if sub is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Suscripción no encontrada",
		)
	return sub


@router.put("/{sub_id}", response_model=SubResponse)
async def replace_sub(
	sub_id: int,
	sub_data: SubCreate,
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
) -> SubResponse:
	sub = await subs_service.update_sub(
		session, current_user.id, sub_id, sub_data
	)
	if sub is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Suscripción no encontrada",
		)
	return sub


@router.delete("/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_sub(
	sub_id: int,
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
) -> None:
	deleted = await subs_service.delete_sub(session, current_user.id, sub_id)
	if not deleted:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Suscripción no encontrada",
		)
