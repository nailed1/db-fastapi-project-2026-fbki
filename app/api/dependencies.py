"""FastAPI dependency injection helpers."""

from typing import AsyncGenerator

import asyncpg
from fastapi import Depends, Request

from app.database import Database, get_pool


async def get_db(request: Request) -> AsyncGenerator[Database, None]:
    pool: asyncpg.Pool = await get_pool()
    yield Database(pool)
