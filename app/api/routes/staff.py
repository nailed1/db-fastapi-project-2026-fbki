"""Staff / manager dashboard routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_db
from app.database import Database

router = APIRouter(prefix="/manager", tags=["manager"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Database = Depends(get_db)) -> HTMLResponse:
    hotel_stats = await db.fetch("""
        SELECT h.name,
               COUNT(b.id) FILTER (WHERE b.status = 'Подтверждено') AS active_bookings,
               COALESCE(SUM(b.total_price) FILTER (WHERE b.status != 'Отменено'), 0) AS revenue,
               COUNT(r.id) FILTER (WHERE r.cleaning_status = 'Dirty') AS dirty_rooms
        FROM hotels h
        LEFT JOIN rooms r    ON r.hotel_id = h.id
        LEFT JOIN bookings b ON b.room_id  = r.id
        GROUP BY h.name ORDER BY h.name
    """)
    recent_bookings = await db.fetch("""
        SELECT b.id, b.check_in, b.check_out, b.status, b.total_price,
               g.full_name AS guest_name, h.name AS hotel_name
        FROM bookings b
        JOIN guests g ON g.id = b.guest_id
        JOIN rooms r  ON r.id = b.room_id
        JOIN hotels h ON h.id = r.hotel_id
        ORDER BY b.id DESC LIMIT 10
    """)
    return templates.TemplateResponse("manager/dashboard.html", {
        "request": request,
        "hotel_stats": hotel_stats,
        "recent_bookings": recent_bookings,
    })


@router.get("/cleaning", response_class=HTMLResponse)
async def cleaning_tasks(request: Request, db: Database = Depends(get_db)) -> HTMLResponse:
    tasks = await db.fetch("""
        SELECT r.id, r.room_number, r.cleaning_status, h.name AS hotel_name
        FROM rooms r
        JOIN hotels h ON h.id = r.hotel_id
        WHERE r.cleaning_status IN ('Dirty', 'Cleaning')
        ORDER BY h.name, r.room_number
    """)
    return templates.TemplateResponse(
        "manager/cleaning.html", {"request": request, "tasks": tasks}
    )
