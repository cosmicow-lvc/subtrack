from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.charges import ChargeCreate, ChargeResponse
from app.services import charges as charges_service


router = APIRouter(prefix="/charges", tags=["charges"])


@router.post(
	"",
	response_model=ChargeResponse,
	status_code=status.HTTP_201_CREATED,
)
async def create_charge(
	charge_data: ChargeCreate,
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
) -> ChargeResponse:
	try:
		return await charges_service.create_charge(
			session, current_user.id, charge_data
		)
	except charges_service.SubscriptionNotFoundError as exc:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Suscripción no encontrada",
		) from exc


@router.get("", response_model=list[ChargeResponse])
async def list_charges(
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
	limit: Annotated[int, Query(ge=1, le=100)] = 50,
	offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ChargeResponse]:
	return await charges_service.list_charges(
		session, current_user.id, limit, offset
	)


@router.get("/{charge_id}", response_model=ChargeResponse)
async def read_charge(
	charge_id: int,
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
) -> ChargeResponse:
	charge = await charges_service.get_charge(session, current_user.id, charge_id)
	if charge is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Cargo no encontrado",
		)
	return charge


@router.delete("/{charge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_charge(
	charge_id: int,
	session: Annotated[AsyncSession, Depends(get_db_session)],
	current_user: Annotated[User, Depends(get_current_user)],
) -> None:
	deleted = await charges_service.delete_charge(
		session, current_user.id, charge_id
	)
	if not deleted:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Cargo no encontrado",
		)
