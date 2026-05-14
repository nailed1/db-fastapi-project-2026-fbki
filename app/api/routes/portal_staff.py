"""Staff portal — tasks, cleaning, replenishment requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_db
from app.auth.dependencies import CurrentUser, require_staff
from app.database import Database

router = APIRouter(prefix="/portal/staff", tags=["staff"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: CurrentUser = Depends(require_staff),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    # Cleaning tasks for this staff member's hotel
    dirty_rooms = await db.fetch("""
        SELECT r.id, r.room_number, r.cleaning_status, h.name AS hotel_name
        FROM rooms r JOIN hotels h ON h.id = r.hotel_id
        WHERE r.hotel_id = $1 AND r.cleaning_status IN ('Dirty','Cleaning')
        ORDER BY r.room_number
    """, user.hotel_id)

    # My replenishment requests
    my_requests = await db.fetch("""
        SELECT id, item_name, quantity, unit, status, created_at
        FROM replenishment_requests
        WHERE staff_id = $1
        ORDER BY created_at DESC LIMIT 10
    """, user.id)

    # Today's schedule
    schedule = await db.fetchrow("""
        SELECT shift, note FROM staff_schedules
        WHERE staff_id = $1 AND work_date = CURRENT_DATE
    """, user.id)

    return templates.TemplateResponse("portal/staff/dashboard.html", {
        "request": request, "current_user": user, "user": user,
        "dirty_rooms": dirty_rooms,
        "my_requests": my_requests,
        "schedule": schedule,
    })


@router.post("/clean/{room_id}", response_class=HTMLResponse)
async def mark_clean(
    room_id: int,
    user: CurrentUser = Depends(require_staff),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    await db.execute(
        "UPDATE rooms SET cleaning_status = 'Clean' WHERE id = $1 AND hotel_id = $2",
        room_id, user.hotel_id,
    )
    return RedirectResponse(url="/portal/staff/", status_code=303)


@router.post("/replenishment", response_class=HTMLResponse)
async def request_replenishment(
    item_name: str = Form(...),
    quantity: int = Form(...),
    unit: str = Form("шт"),
    user: CurrentUser = Depends(require_staff),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    await db.execute("""
        INSERT INTO replenishment_requests (staff_id, hotel_id, item_name, quantity, unit)
        VALUES ($1, $2, $3, $4, $5)
    """, user.id, user.hotel_id, item_name, quantity, unit)
    return RedirectResponse(url="/portal/staff/", status_code=303)
