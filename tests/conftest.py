import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI

os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_DB"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"
os.environ["CORS_ORIGINS"] = '["http://localhost"]'

from app.main import app


@asynccontextmanager
async def test_lifespan(_: FastAPI) -> AsyncIterator[None]:
	yield


@pytest.fixture(autouse=True)
def disable_app_lifespan(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(app.router, "lifespan_context", test_lifespan)