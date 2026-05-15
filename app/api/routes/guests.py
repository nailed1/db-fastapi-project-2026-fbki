"""Guest routes — list and create."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_db
from app.auth.dependencies import CurrentUser, get_current_user
from app.database import Database

router = APIRouter(prefix="/guests", tags=["guests"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_guests(
    request: Request,
    db: Database = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
) -> HTMLResponse:
    rows = await db.fetch("""
        SELECT id, full_name, phone, email, loyalty_tier, total_spend
        FROM guests ORDER BY full_name
    """)
    return templates.TemplateResponse(
        "guests/list.html",
        {"request": request, "current_user": current_user, "guests": rows},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_guest_form(
    request: Request,
    current_user: CurrentUser | None = Depends(get_current_user),
) -> HTMLResponse:
    return templates.TemplateResponse(
        "guests/create.html",
        {"request": request, "current_user": current_user},
    )


@router.post("/", response_class=HTMLResponse)
async def create_guest(
    request: Request,
    full_name: str = Form(...),
    passport: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    await db.execute("""
        INSERT INTO guests (full_name, passport, phone, email)
        VALUES ($1, $2, $3, $4)
    """, full_name, passport, phone or None, email or None)
    return RedirectResponse(url="/guests/", status_code=303)
