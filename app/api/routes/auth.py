"""Login / logout / registration routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

from app.api.dependencies import get_db
from app.auth.dependencies import CurrentUser, get_current_user
from app.auth.flash import flash
from app.auth.jwt import create_access_token
from app.database import Database

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _safe_verify(password: str, hash_: str) -> bool:
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
    # Try tourist
    tourist = await db.fetchrow(
        "SELECT u.id, u.password_hash FROM users u WHERE u.login = $1", login
    )
    if tourist and _safe_verify(password, tourist["password_hash"]):
        token = create_access_token({"sub": str(tourist["id"]), "type": "tourist"})
        resp = RedirectResponse(url="/portal/tourist/", status_code=303)
        resp.set_cookie("access_token", token, httponly=True, max_age=3600 * 8, samesite="lax")
        flash(resp, "Добро пожаловать!", "success")
        return resp

    # Try staff
    staff_row = await db.fetchrow(
        "SELECT id, password_hash, role FROM staff WHERE login = $1", login
    )
    if staff_row and _safe_verify(password, staff_row["password_hash"]):
        token = create_access_token({"sub": str(staff_row["id"]), "type": "staff"})
        from app.auth.dependencies import _db_role_to_system
        role = _db_role_to_system(staff_row["role"])
        resp = RedirectResponse(url=_home_for(role), status_code=303)
        resp.set_cookie("access_token", token, httponly=True, max_age=3600 * 8, samesite="lax")
        flash(resp, f"Добро пожаловать, {staff_row['role']}!", "success")
        return resp

    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "error": "Неверный логин или пароль"},
        status_code=401,
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    user: CurrentUser | None = Depends(get_current_user),
) -> HTMLResponse:
    if user:
        return RedirectResponse(url=_home_for(user.system_role), status_code=302)
    return templates.TemplateResponse("auth/register.html", {"request": request, "error": None})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    full_name: str = Form(...),
    passport: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    login: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    def err(msg: str) -> HTMLResponse:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": msg,
             "form": {"full_name": full_name, "passport": passport,
                      "phone": phone, "email": email, "login": login}},
            status_code=400,
        )

    if password != password_confirm:
        return err("Пароли не совпадают")
    if len(password) < 6:
        return err("Пароль должен быть не короче 6 символов")

    exists = await db.fetchval("SELECT 1 FROM users WHERE login = $1", login)
    if exists:
        return err("Логин уже занят")

    passport_taken = await db.fetchval("SELECT 1 FROM guests WHERE passport = $1", passport)
    if passport_taken:
        return err("Гость с таким паспортом уже существует — войдите вместо регистрации")

    # Create guest + user
    guest_id = await db.fetchval("""
        INSERT INTO guests (full_name, passport, phone, email)
        VALUES ($1, $2, $3, $4) RETURNING id
    """, full_name, passport, phone or None, email or None)

    user_id = await db.fetchval("""
        INSERT INTO users (guest_id, login, password_hash)
        VALUES ($1, $2, $3) RETURNING id
    """, guest_id, login, pwd_ctx.hash(password))

    token = create_access_token({"sub": str(user_id), "type": "tourist"})
    resp = RedirectResponse(url="/portal/tourist/", status_code=303)
    resp.set_cookie("access_token", token, httponly=True, max_age=3600 * 8, samesite="lax")
    flash(resp, "Регистрация успешна! Добро пожаловать.", "success")
    return resp


@router.post("/logout")
async def logout() -> RedirectResponse:
    resp = RedirectResponse(url="/auth/login", status_code=303)
    resp.delete_cookie("access_token")
    flash(resp, "Вы вышли из системы", "info")
    return resp


def _home_for(role: str) -> str:
    return {
        "tourist": "/portal/tourist/",
        "staff":   "/portal/staff/",
        "manager": "/portal/manager/",
        "admin":   "/portal/admin/",
    }.get(role, "/auth/login")
