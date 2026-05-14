"""Role-based FastAPI dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.auth.jwt import decode_token
from app.database import Database, get_pool
import asyncpg

# System role derived from DB role field
STAFF_ROLES = {"Горничная", "Уборщик", "Сантехник", "Бармен", "Техник"}
MANAGER_ROLES = {"Менеджер"}
ADMIN_ROLES = {"Администратор"}

SystemRole = Literal["tourist", "staff", "manager", "admin"]


@dataclass
class CurrentUser:
    id: int
    login: str
    full_name: str
    system_role: SystemRole
    hotel_id: int | None = None
    db_role: str | None = None  # specific staff role e.g. "Уборщик"


def _db_role_to_system(db_role: str) -> SystemRole:
    if db_role in ADMIN_ROLES:
        return "admin"
    if db_role in MANAGER_ROLES:
        return "manager"
    if db_role in STAFF_ROLES:
        return "staff"
    return "tourist"


async def get_db_for_auth() -> Database:
    pool: asyncpg.Pool = await get_pool()
    return Database(pool)


async def get_current_user(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: Database = Depends(get_db_for_auth),
) -> CurrentUser | None:
    """Return current user from JWT cookie, or None if not authenticated."""
    if not access_token:
        return None
    payload = decode_token(access_token)
    if not payload:
        return None

    user_type = payload.get("type")  # "tourist" or "staff"
    user_id = payload.get("sub")
    if not user_id:
        return None

    if user_type == "tourist":
        row = await db.fetchrow("""
            SELECT u.id, u.login, g.full_name
            FROM users u
            JOIN guests g ON g.id = u.guest_id
            WHERE u.id = $1
        """, int(user_id))
        if not row:
            return None
        return CurrentUser(
            id=int(user_id),
            login=row["login"],
            full_name=row["full_name"],
            system_role="tourist",
        )
    else:
        row = await db.fetchrow("""
            SELECT id, login, full_name, role, hotel_id
            FROM staff WHERE id = $1
        """, int(user_id))
        if not row:
            return None
        return CurrentUser(
            id=row["id"],
            login=row["login"],
            full_name=row["full_name"],
            system_role=_db_role_to_system(row["role"]),
            hotel_id=row["hotel_id"],
            db_role=row["role"],
        )


async def require_tourist(
    user: CurrentUser | None = Depends(get_current_user),
) -> CurrentUser:
    if not user or user.system_role != "tourist":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tourist access required")
    return user


async def require_staff(
    user: CurrentUser | None = Depends(get_current_user),
) -> CurrentUser:
    if not user or user.system_role not in ("staff", "manager", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required")
    return user


async def require_manager(
    user: CurrentUser | None = Depends(get_current_user),
) -> CurrentUser:
    if not user or user.system_role not in ("manager", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager access required")
    return user


async def require_admin(
    user: CurrentUser | None = Depends(get_current_user),
) -> CurrentUser:
    if not user or user.system_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
