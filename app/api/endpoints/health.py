from fastapi import APIRouter, status


router = APIRouter(tags=["health"])


@router.get(
	"/health",
	response_model=dict[str, str],
	status_code=status.HTTP_200_OK,
)
async def healthcheck() -> dict[str, str]:
	return {"status": "ok"}