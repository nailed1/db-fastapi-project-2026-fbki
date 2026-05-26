"""Booking routes — CRUD + availability check."""

from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_db
from app.auth.dependencies import CurrentUser, get_current_user
from app.database import Database
from hotel_utils import DateRange, calculate_price, discount_for_tier, is_available, tier_from_spend

router = APIRouter(prefix="/bookings", tags=["bookings"])
templates = Jinja2Templates(directory="app/templates")

from typing import Optional

@router.get("/", response_class=HTMLResponse)
async def list_bookings(
    request: Request,
    db: Database = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
) -> HTMLResponse:
    rows = await db.fetch("""
        SELECT b.id, b.check_in, b.check_out, b.total_price, b.status,
               g.full_name AS guest_name,
               r.room_number,
               h.name AS hotel_name
        FROM bookings b
        JOIN guests g ON g.id = b.guest_id
        JOIN rooms  r ON r.id = b.room_id
        JOIN hotels h ON h.id = r.hotel_id
        ORDER BY b.check_in DESC
    """)
    return templates.TemplateResponse(
        "booking/list.html",
        {"request": request, "current_user": current_user, "bookings": rows},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_booking_form(
    request: Request,
    db: Database = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_current_user),
) -> HTMLResponse:
    hotels = await db.fetch("SELECT id, name FROM hotels ORDER BY name")
    guests = await db.fetch("SELECT id, full_name FROM guests ORDER BY full_name")
    return templates.TemplateResponse(
        "booking/create.html",
        {"request": request, "current_user": current_user,
         "hotels": hotels, "guests": guests},
    )


@router.get("/available-rooms")
async def available_rooms(
    hotel_id: Optional[str] = None,
    check_in: Optional[str] = None,
    check_out: Optional[str] = None,
    db: Database = Depends(get_db),
) -> list[dict]:
    
    if not hotel_id or not check_in or not check_out:
        return []

    try:
        parsed_hotel_id = int(hotel_id)
        parsed_check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
        parsed_check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
    except ValueError:
        return []

    rows = await db.fetch("""
        SELECT r.id, r.room_number, rc.name AS category, rc.base_price
        FROM rooms r
        JOIN room_categories rc ON rc.id = r.category_id
        WHERE r.hotel_id = $1
          AND r.room_condition = 'Исправно'
          AND r.id NOT IN (
              SELECT room_id FROM bookings
              WHERE status IN ('Подтверждено', 'Ожидает оплаты')
                AND check_in  < $3
                AND check_out > $2
          )
        ORDER BY rc.base_price
    """, parsed_hotel_id, parsed_check_in, parsed_check_out)
    
    return [dict(r) for r in rows]


@router.post("/", response_class=HTMLResponse)
async def create_booking(
    request: Request,
    guest_id: int = Form(...),
    room_id: int = Form(...),
    check_in: date = Form(...),
    check_out: date = Form(...),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    # Check no overlap
    existing_rows = await db.fetch("""
        SELECT check_in, check_out FROM bookings
        WHERE room_id = $1 AND status IN ('Подтверждено', 'Ожидает оплаты')
    """, room_id)
    requested = DateRange(check_in, check_out)
    occupied = [DateRange(r["check_in"], r["check_out"]) for r in existing_rows]
    if not is_available(requested, occupied):
        raise HTTPException(status_code=409, detail="Room is not available for selected dates")

    # Calculate price
    guest = await db.fetchrow(
        "SELECT loyalty_tier, total_spend FROM guests WHERE id = $1", guest_id
    )
    room = await db.fetchrow("""
        SELECT rc.base_price FROM rooms r
        JOIN room_categories rc ON rc.id = r.category_id
        WHERE r.id = $1
    """, room_id)

    tier = tier_from_spend(Decimal(str(guest["total_spend"])))
    discount = discount_for_tier(tier)
    total = calculate_price(
        base_price=Decimal(str(room["base_price"])),
        check_in=check_in,
        check_out=check_out,
        loyalty_discount=discount,
    )

    booking_id = await db.fetchval("""
        INSERT INTO bookings (guest_id, room_id, check_in, check_out, total_price, status)
        VALUES ($1, $2, $3, $4, $5, 'Подтверждено')
        RETURNING id
    """, guest_id, room_id, check_in, check_out, total)

    # Update guest total_spend
    await db.execute(
        "UPDATE guests SET total_spend = total_spend + $1 WHERE id = $2", total, guest_id
    )
    # Re-calculate loyalty tier
    updated_guest = await db.fetchrow("SELECT total_spend FROM guests WHERE id = $1", guest_id)
    new_tier = tier_from_spend(Decimal(str(updated_guest["total_spend"])))
    await db.execute(
        "UPDATE guests SET loyalty_tier = $1 WHERE id = $2", new_tier.value, guest_id
    )

    # Audit log
    await db.execute("""
        INSERT INTO audit_log (table_name, new_value) VALUES ('bookings', $1)
    """, f"Created booking #{booking_id} for guest #{guest_id}")

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/bookings/", status_code=303)


@router.post("/{booking_id}/cancel", response_class=HTMLResponse)
async def cancel_booking(
    booking_id: int, db: Database = Depends(get_db)
) -> HTMLResponse:
    await db.execute(
        "UPDATE bookings SET status = 'Отменено' WHERE id = $1", booking_id
    )
    await db.execute("""
        INSERT INTO audit_log (table_name, new_value) VALUES ('bookings', $1)
    """, f"Cancelled booking #{booking_id}")
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/bookings/", status_code=303)
