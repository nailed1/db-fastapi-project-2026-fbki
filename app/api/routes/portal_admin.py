"""Admin portal — system management, service requests to manager."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_db
from app.auth.dependencies import CurrentUser, require_admin
from app.database import Database

router = APIRouter(prefix="/portal/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: CurrentUser = Depends(require_admin),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    hotels = await db.fetch("""
        SELECT h.id, h.name,
               COUNT(DISTINCT r.id)  AS total_rooms,
               COUNT(DISTINCT s.id)  AS total_staff,
               COUNT(DISTINCT b.id) FILTER (WHERE b.status IN ('Подтверждено', 'Ожидает оплаты')) AS active_bookings
        FROM hotels h
        LEFT JOIN rooms r    ON r.hotel_id = h.id
        LEFT JOIN staff s    ON s.hotel_id = h.id
        LEFT JOIN bookings b ON b.room_id = r.id
        GROUP BY h.id, h.name ORDER BY h.name
    """)

    my_requests = await db.fetch("""
        SELECT sr.id, sr.description, sr.status, sr.created_at,
               s.full_name AS manager_name, h.name AS hotel_name
        FROM service_requests sr
        JOIN hotels h ON h.id = sr.hotel_id
        LEFT JOIN staff s ON s.id = sr.manager_id
        WHERE sr.admin_id = $1
        ORDER BY sr.created_at DESC
    """, user.id)

    audit = await db.fetch("""
        SELECT al.table_name, al.new_value, al.changed_at,
               s.full_name AS staff_name
        FROM audit_log al
        LEFT JOIN staff s ON s.id = al.staff_id
        ORDER BY al.changed_at DESC LIMIT 30
    """)

    managers = await db.fetch("""
        SELECT id, full_name, hotel_id FROM staff WHERE role = 'Менеджер'
    """)

    return templates.TemplateResponse("portal/admin/dashboard.html", {
        "request": request, "current_user": user, "user": user,
        "hotels": hotels, "my_requests": my_requests,
        "audit": audit, "managers": managers,
    })


@router.post("/service-request", response_class=HTMLResponse)
async def create_service_request(
    hotel_id: int = Form(...),
    manager_id: int | None = Form(None),
    description: str = Form(...),
    user: CurrentUser = Depends(require_admin),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    await db.execute("""
        INSERT INTO service_requests (admin_id, manager_id, hotel_id, description)
        VALUES ($1, $2, $3, $4)
    """, user.id, manager_id or None, hotel_id, description)

    await db.execute("""
        INSERT INTO audit_log (staff_id, table_name, new_value)
        VALUES ($1, 'service_requests', $2)
    """, user.id, f"Admin #{user.id} создал запрос на обслуживание для отеля #{hotel_id}")

    return RedirectResponse(url="/portal/admin/", status_code=303)


@router.get("/users", response_class=HTMLResponse)
async def user_management(
    request: Request,
    user: CurrentUser = Depends(require_admin),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    staff_list = await db.fetch("""
        SELECT s.id, s.full_name, s.role, s.login, h.name AS hotel_name
        FROM staff s LEFT JOIN hotels h ON h.id = s.hotel_id
        ORDER BY s.role, s.full_name
    """)
    tourists = await db.fetch("""
        SELECT u.id, u.login, g.full_name, g.loyalty_tier, g.total_spend
        FROM users u JOIN guests g ON g.id = u.guest_id
        ORDER BY g.full_name
    """)
    hotels = await db.fetch("SELECT id, name FROM hotels ORDER BY name")
    return templates.TemplateResponse("portal/admin/users.html", {
        "request": request, "current_user": user, "user": user,
        "staff_list": staff_list, "tourists": tourists, "hotels": hotels,
    })


@router.post("/staff/create", response_class=HTMLResponse)
async def create_staff(
    hotel_id: int = Form(...),
    full_name: str = Form(...),
    role: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    user: CurrentUser = Depends(require_admin),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_ctx.hash(password)
    await db.execute("""
        INSERT INTO staff (hotel_id, full_name, role, login, password_hash)
        VALUES ($1, $2, $3, $4, $5)
    """, hotel_id, full_name, role, login, hashed)
    return RedirectResponse(url="/portal/admin/users", status_code=303)
