from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed import seed_demo_data


@pytest.mark.asyncio
async def test_seed_skips_existing_demo_account():
	session = AsyncMock(spec=AsyncSession)
	session.scalar.return_value = 1

	await seed_demo_data(session)

	session.add.assert_not_called()
	session.add_all.assert_not_called()
	session.commit.assert_not_awaited()