"""Run SQL migrations from the migrations/ directory."""

import asyncio
import pathlib

import asyncpg

from app.config import settings

MIGRATIONS_DIR = pathlib.Path(__file__).parent.parent.parent / "migrations"


async def run_migrations() -> None:
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn=dsn)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT NOW()
            )
        """)
        applied: set[str] = {
            r["filename"] for r in await conn.fetch("SELECT filename FROM _migrations")
        }
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if sql_file.name in applied:
                print(f"  skip  {sql_file.name}")
                continue
            print(f"  apply {sql_file.name}")
            sql = sql_file.read_text(encoding="utf-8")
            await conn.execute(sql)
            await conn.execute(
                "INSERT INTO _migrations (filename) VALUES ($1)", sql_file.name
            )
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())
