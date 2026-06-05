"""Integration tests: PostgreSQL with migrations (CI / make test-integration)."""

import os
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Default test DB when DATABASE_URL is unset (CI sets this at job level).
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://hotel_user:hotel_pass@localhost:5432/hotel_test",
)

from app.database import close_pool  # noqa: E402
from app.main import app  # noqa: E402


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # Сброс пула между тестами — иначе asyncpg привязан к закрытому event loop.
    await close_pool()
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac
    await close_pool()
