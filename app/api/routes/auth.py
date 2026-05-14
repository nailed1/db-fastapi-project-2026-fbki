"""Login / logout routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

from app.api.dependencies import get_db
from app.auth.dependencies import CurrentUser, get_current_user
from app.auth.jwt import create_access_token
from app.database import Database

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _safe_verify(password: str, hash_: str) -> bool:
    """Verify password, returning False on any error (e.g. invalid hash format)."""
    try:
        return pwd_ctx.verify(password, hash_)
    except Exception:
        return False


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: CurrentUser | None = Depends(get_current_user),
) -> HTMLResponse:
    if user:
        return RedirectResponse(url=_home_for(user.system_role), status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    error = "Неверный логин или пароль"

    # Try tourist login first
    tourist = await db.fetchrow(
        "SELECT u.id, u.password_hash FROM users u WHERE u.login = $1", login
    )
    if tourist and _safe_verify(password, tourist["password_hash"]):
        token = create_access_token({"sub": str(tourist["id"]), "type": "tourist"})
        resp = RedirectResponse(url="/portal/tourist/", status_code=303)
        resp.set_cookie("access_token", token, httponly=True, max_age=3600 * 8, samesite="lax")
        return resp

    # Try staff login
    staff_row = await db.fetchrow(
        "SELECT id, password_hash, role FROM staff WHERE login = $1", login
    )
    if staff_row and _safe_verify(password, staff_row["password_hash"]):
        token = create_access_token({"sub": str(staff_row["id"]), "type": "staff"})
        from app.auth.dependencies import _db_role_to_system
        role = _db_role_to_system(staff_row["role"])
        resp = RedirectResponse(url=_home_for(role), status_code=303)
        resp.set_cookie("access_token", token, httponly=True, max_age=3600 * 8, samesite="lax")
        return resp

    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "error": error}, status_code=401
    )


@router.post("/logout")
async def logout() -> RedirectResponse:
    resp = RedirectResponse(url="/auth/login", status_code=303)
    resp.delete_cookie("access_token")
    return resp


def _home_for(role: str) -> str:
    return {
        "tourist": "/portal/tourist/",
        "staff":   "/portal/staff/",
        "manager": "/portal/manager/",
        "admin":   "/portal/admin/",
    }.get(role, "/auth/login")
