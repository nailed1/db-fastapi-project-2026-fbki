"""Integration test fixtures — spins up a real test DB via docker-compose."""

import asyncio
from typing import AsyncGenerator

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app

TEST_DSN = "postgresql://hotel_user:hotel_pass@localhost:5432/hotel_test"


@pytest_asyncio.fixture(scope="session")
async def db_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    pool = await asyncpg.create_pool(dsn=TEST_DSN, min_size=1, max_size=5)
    yield pool
    await pool.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
