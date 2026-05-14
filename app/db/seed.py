"""Apply seed data (migration 002_seed.sql) standalone."""

import asyncio
import pathlib

import asyncpg

from app.config import settings

SEED_FILE = pathlib.Path(__file__).parent.parent.parent / "migrations" / "002_seed.sql"


async def seed() -> None:
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn=dsn)
    try:
        sql = SEED_FILE.read_text(encoding="utf-8")
        # Only execute DML lines (skip comment-only query examples)
        await conn.execute(sql)
        print("Seed data applied.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
