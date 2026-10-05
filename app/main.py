from collections.abc import AsyncIterator

from fastapi import FastAPI
from sqlalchemy import inspect, text

from app import models
from app.api.endpoints.health import router as health_router
from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.seed import seed_demo_data
from app.db.session import AsyncSessionLocal, engine

async def lifespan(_: FastAPI) -> AsyncIterator[None]:
	"""Crea las tablas que aún no existen al iniciar la aplicación."""
	_ = models
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)
		columns = await connection.run_sync(
			lambda sync_connection: inspect(sync_connection).get_columns(
				"subscriptions"
			)
		)
		if not any(column["name"] == "is_active" for column in columns):
			await connection.execute(
				text(
					"ALTER TABLE subscriptions ADD COLUMN is_active "
					"BOOLEAN NOT NULL DEFAULT TRUE"
				)
			)
	if settings.ENVIRONMENT == "local":
		async with AsyncSessionLocal() as session:
			await seed_demo_data(session)
	try:
		yield
	finally:
		await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_PREFIX)