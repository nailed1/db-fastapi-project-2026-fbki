"""
Set bcrypt passwords for demo accounts.
Runs once at startup if any staff hash looks like a placeholder.

Demo credentials:
  Staff / Manager / Admin : password123
  Tourist                 : tourist123
"""

import asyncio

import asyncpg
from passlib.context import CryptContext

from app.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

STAFF_PASSWORD  = "password123"
TOURIST_PASSWORD = "tourist123"


async def setup() -> None:
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn=dsn)
    try:
        staff_hash    = pwd_ctx.hash(STAFF_PASSWORD)
        tourist_hash  = pwd_ctx.hash(TOURIST_PASSWORD)

        # Update ALL staff with placeholder or invalid hashes
        rows = await conn.fetch("SELECT id, password_hash FROM staff")
        updated = 0
        for row in rows:
            try:
                pwd_ctx.verify("test", row["password_hash"])
            except Exception:
                # Invalid hash — replace it
                await conn.execute(
                    "UPDATE staff SET password_hash = $1 WHERE id = $2",
                    staff_hash, row["id"],
                )
                updated += 1
        if updated:
            print(f"  passwords  reset {updated} staff account(s) → '{STAFF_PASSWORD}'")

        # Set tourist demo password
        await conn.execute("""
            UPDATE users SET password_hash = $1
            WHERE login = 'tourist1'
        """, tourist_hash)
        print(f"  passwords  tourist1 → '{TOURIST_PASSWORD}'")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(setup())
