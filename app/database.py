"""Async database access via asyncpg connection pool."""

from __future__ import annotations

import asyncpg

from app.config import settings

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        # Strip the SQLAlchemy prefix if present
        dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        _pool = await asyncpg.create_pool(dsn=dsn, min_size=2, max_size=10)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_connection() -> asyncpg.Connection:
    pool = await get_pool()
    return await pool.acquire()


class Database:
    """Thin wrapper providing query helpers used across route handlers."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def fetch(self, query: str, *args: object) -> list[asyncpg.Record]:
        return await self._pool.fetch(query, *args)

    async def fetchrow(self, query: str, *args: object) -> asyncpg.Record | None:
        return await self._pool.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: object) -> object:
        return await self._pool.fetchval(query, *args)

    async def execute(self, query: str, *args: object) -> str:
        return await self._pool.execute(query, *args)
