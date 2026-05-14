"""Tourist portal — booking, reviews, profile."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_db
from app.auth.dependencies import CurrentUser, require_tourist
from app.database import Database
from hotel_utils import DateRange, calculate_price, discount_for_tier, is_available, tier_from_spend

router = APIRouter(prefix="/portal/tourist", tags=["tourist"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    # Get guest linked to this user
    guest = await db.fetchrow("""
        SELECT g.id, g.full_name, g.loyalty_tier, g.total_spend
        FROM users u JOIN guests g ON g.id = u.guest_id
        WHERE u.id = $1
    """, user.id)

    bookings = await db.fetch("""
        SELECT b.id, b.check_in, b.check_out, b.total_price, b.status,
               h.name AS hotel_name, r.room_number, rc.name AS category
        FROM bookings b
        JOIN rooms r ON r.id = b.room_id
        JOIN hotels h ON h.id = r.hotel_id
        JOIN room_categories rc ON rc.id = r.category_id
        WHERE b.guest_id = $1
        ORDER BY b.check_in DESC LIMIT 10
    """, guest["id"])

    hotels = await db.fetch("""
        SELECT h.id, h.name, h.address,
               COALESCE(ROUND(AVG(rv.rating), 1), 0) AS avg_rating,
               COUNT(rv.id) AS review_count
        FROM hotels h
        LEFT JOIN reviews rv ON rv.hotel_id = h.id
        GROUP BY h.id, h.name, h.address
        ORDER BY h.name
    """)

    return templates.TemplateResponse("portal/tourist/dashboard.html", {
        "request": request, "current_user": user, "user": user, "guest": guest,
        "bookings": bookings, "hotels": hotels,
    })


@router.get("/book", response_class=HTMLResponse)
async def booking_form(
    request: Request,
    hotel_id: int | None = None,
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    hotels = await db.fetch("SELECT id, name, address FROM hotels ORDER BY name")
    selected_hotel = None
    if hotel_id:
        selected_hotel = await db.fetchrow("SELECT id, name FROM hotels WHERE id = $1", hotel_id)
    return templates.TemplateResponse("portal/tourist/book.html", {
        "request": request, "current_user": user, "user": user,
        "hotels": hotels, "selected_hotel": selected_hotel,
    })


@router.post("/book", response_class=HTMLResponse)
async def create_booking(
    request: Request,
    hotel_id: int = Form(...),
    room_id: int = Form(...),
    check_in: date = Form(...),
    check_out: date = Form(...),
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    guest = await db.fetchrow("""
        SELECT g.id, g.loyalty_tier, g.total_spend
        FROM users u JOIN guests g ON g.id = u.guest_id WHERE u.id = $1
    """, user.id)

    # Availability check
    existing = await db.fetch("""
        SELECT check_in, check_out FROM bookings
        WHERE room_id = $1 AND status = 'Подтверждено'
    """, room_id)
    requested = DateRange(check_in, check_out)
    if not is_available(requested, [DateRange(r["check_in"], r["check_out"]) for r in existing]):
        raise HTTPException(409, "Номер недоступен на выбранные даты")

    # Price calc
    room = await db.fetchrow("""
        SELECT rc.base_price FROM rooms r
        JOIN room_categories rc ON rc.id = r.category_id WHERE r.id = $1
    """, room_id)
    tier = tier_from_spend(Decimal(str(guest["total_spend"])))
    total = calculate_price(
        base_price=Decimal(str(room["base_price"])),
        check_in=check_in, check_out=check_out,
        loyalty_discount=discount_for_tier(tier),
    )

    booking_id = await db.fetchval("""
        INSERT INTO bookings (guest_id, room_id, check_in, check_out, total_price, status)
        VALUES ($1, $2, $3, $4, $5, 'Подтверждено') RETURNING id
    """, guest["id"], room_id, check_in, check_out, total)

    await db.execute(
        "UPDATE guests SET total_spend = total_spend + $1 WHERE id = $2", total, guest["id"]
    )
    new_tier = tier_from_spend(Decimal(str(guest["total_spend"])) + total)
    await db.execute(
        "UPDATE guests SET loyalty_tier = $1 WHERE id = $2", new_tier.value, guest["id"]
    )
    await db.execute(
        "UPDATE rooms SET cleaning_status = 'Dirty' WHERE id = $1", room_id
    )

    return RedirectResponse(url="/portal/tourist/", status_code=303)


@router.get("/review/{booking_id}", response_class=HTMLResponse)
async def review_form(
    request: Request,
    booking_id: int,
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    booking = await db.fetchrow("""
        SELECT b.id, b.status, b.check_out, h.id AS hotel_id, h.name AS hotel_name,
               r.room_number
        FROM bookings b
        JOIN guests g ON g.id = b.guest_id
        JOIN users u  ON u.guest_id = g.id
        JOIN rooms r  ON r.id = b.room_id
        JOIN hotels h ON h.id = r.hotel_id
        WHERE b.id = $1 AND u.id = $2
    """, booking_id, user.id)
    if not booking:
        raise HTTPException(404, "Бронирование не найдено")
    if booking["status"] != "Завершено":
        raise HTTPException(400, "Отзыв можно оставить только после завершения проживания")

    existing = await db.fetchrow("SELECT id FROM reviews WHERE booking_id = $1", booking_id)
    return templates.TemplateResponse("portal/tourist/review.html", {
        "request": request, "current_user": user, "user": user,
        "booking": booking, "has_review": existing is not None,
    })


@router.post("/review/{booking_id}", response_class=HTMLResponse)
async def submit_review(
    booking_id: int,
    rating: int = Form(...),
    comment: str = Form(""),
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    booking = await db.fetchrow("""
        SELECT b.id, b.status, g.id AS guest_id, r.hotel_id
        FROM bookings b
        JOIN guests g ON g.id = b.guest_id
        JOIN users u  ON u.guest_id = g.id
        JOIN rooms r  ON r.id = b.room_id
        WHERE b.id = $1 AND u.id = $2
    """, booking_id, user.id)
    if not booking or booking["status"] != "Завершено":
        raise HTTPException(400, "Невозможно оставить отзыв")

    await db.execute("""
        INSERT INTO reviews (booking_id, guest_id, hotel_id, rating, comment)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (booking_id) DO UPDATE SET rating = $4, comment = $5
    """, booking_id, booking["guest_id"], booking["hotel_id"], rating, comment or None)

    return RedirectResponse(url="/portal/tourist/", status_code=303)
