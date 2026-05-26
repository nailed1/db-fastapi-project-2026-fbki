"""Manager portal — staff schedules, bookings, service requests, replenishment orders."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_db
from app.auth.dependencies import CurrentUser, require_manager
from app.database import Database

router = APIRouter(prefix="/portal/manager", tags=["manager"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: CurrentUser = Depends(require_manager),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    # KPIs for manager's hotel
    stats = await db.fetchrow("""
        SELECT
            COUNT(b.id) FILTER (WHERE b.status IN ('Подтверждено', 'Ожидает оплаты')) AS active_bookings,
            COALESCE(SUM(b.total_price) FILTER (WHERE b.status != 'Отменено'), 0) AS revenue,
            COUNT(r.id) FILTER (WHERE r.cleaning_status = 'Dirty') AS dirty_rooms,
            COUNT(sr.id) FILTER (WHERE sr.status = 'Новый') AS new_service_requests,
            COUNT(rr.id) FILTER (WHERE rr.status = 'Новый') AS new_replenish
        FROM hotels h
        LEFT JOIN rooms r    ON r.hotel_id = h.id
        LEFT JOIN bookings b ON b.room_id = r.id
        LEFT JOIN service_requests sr ON sr.hotel_id = h.id
        LEFT JOIN replenishment_requests rr ON rr.hotel_id = h.id
        WHERE h.id = $1
    """, user.hotel_id)

    service_requests = await db.fetch("""
        SELECT sr.id, sr.description, sr.status, sr.created_at,
               s.full_name AS admin_name
        FROM service_requests sr
        JOIN staff s ON s.id = sr.admin_id
        WHERE sr.hotel_id = $1
        ORDER BY sr.created_at DESC LIMIT 20
    """, user.hotel_id)

    replenish_requests = await db.fetch("""
        SELECT rr.id, rr.item_name, rr.quantity, rr.unit, rr.status, rr.created_at,
               s.full_name AS staff_name, s.role AS staff_role
        FROM replenishment_requests rr
        JOIN staff s ON s.id = rr.staff_id
        WHERE rr.hotel_id = $1
        ORDER BY rr.created_at DESC LIMIT 20
    """, user.hotel_id)

    return templates.TemplateResponse("portal/manager/dashboard.html", {
        "request": request, "current_user": user, "user": user, "stats": stats,
        "service_requests": service_requests,
        "replenish_requests": replenish_requests,
    })


@router.get("/schedule", response_class=HTMLResponse)
async def schedule(
    request: Request,
    week: date | None = None,
    user: CurrentUser = Depends(require_manager),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    from datetime import timedelta
    today = date.today()
    monday = (week or today) - timedelta(days=(week or today).weekday())
    days = [monday + timedelta(days=i) for i in range(7)]
    sunday = days[-1]

    staff_rows = await db.fetch("""
        SELECT id, full_name, role FROM staff
        WHERE hotel_id = $1 ORDER BY role, full_name
    """, user.hotel_id)

    # Fetch schedules as plain rows (no JSON)
    sched_rows = await db.fetch("""
        SELECT staff_id, work_date, shift, note
        FROM staff_schedules
        WHERE staff_id = ANY($1::int[]) AND work_date BETWEEN $2 AND $3
    """, [r["id"] for r in staff_rows], monday, sunday)

    # Build lookup: staff_id -> {date_iso: {shift, note}}
    sched_map: dict[int, dict[str, dict]] = {}
    for sr in sched_rows:
        sched_map.setdefault(sr["staff_id"], {})[sr["work_date"].isoformat()] = {
            "shift": sr["shift"], "note": sr["note"]
        }

    staff_list = [
        {"id": r["id"], "full_name": r["full_name"], "role": r["role"],
         "schedules": sched_map.get(r["id"], {})}
        for r in staff_rows
    ]

    return templates.TemplateResponse("portal/manager/schedule.html", {
        "request": request, "current_user": user, "user": user,
        "staff_list": staff_list, "days": days,
        "monday": monday,
        "prev_week": (monday - timedelta(days=7)).isoformat(),
        "next_week": (monday + timedelta(days=7)).isoformat(),
    })


@router.post("/schedule", response_class=HTMLResponse)
async def upsert_schedule(
    staff_id: int = Form(...),
    work_date: date = Form(...),
    shift: str = Form(...),
    note: str = Form(""),
    user: CurrentUser = Depends(require_manager),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    await db.execute("""
        INSERT INTO staff_schedules (staff_id, work_date, shift, note)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (staff_id, work_date) DO UPDATE
            SET shift = $3, note = $4
    """, staff_id, work_date, shift, note or None)
    return RedirectResponse(url=f"/portal/manager/schedule?week={work_date}", status_code=303)


@router.post("/service-request/{req_id}/status", response_class=HTMLResponse)
async def update_service_request(
    req_id: int,
    status: str = Form(...),
    user: CurrentUser = Depends(require_manager),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    await db.execute(
        "UPDATE service_requests SET status = $1, manager_id = $2 WHERE id = $3",
        status, user.id, req_id,
    )
    return RedirectResponse(url="/portal/manager/", status_code=303)


@router.post("/replenishment/{req_id}/status", response_class=HTMLResponse)
async def update_replenishment(
    req_id: int,
    status: str = Form(...),
    user: CurrentUser = Depends(require_manager),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    await db.execute(
        "UPDATE replenishment_requests SET status = $1 WHERE id = $2",
        status, req_id,
    )
    return RedirectResponse(url="/portal/manager/", status_code=303)
