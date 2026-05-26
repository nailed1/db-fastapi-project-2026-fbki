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

from app.auth.flash import flash

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
        SELECT h.id, h.name, h.address, h.latitude, h.longitude,
               COALESCE(ROUND(AVG(rv.rating), 1), 0) AS avg_rating,
               COUNT(rv.id) AS review_count
        FROM hotels h
        LEFT JOIN reviews rv ON rv.hotel_id = h.id
        GROUP BY h.id, h.name, h.address, h.latitude, h.longitude
        ORDER BY h.name
    """)

    def to_json_safe(row):
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in dict(row).items()}
    
    return templates.TemplateResponse("portal/tourist/dashboard.html", {
        "request": request, "current_user": user, "user": user, "guest": guest,
        "bookings": bookings, "hotels": [to_json_safe(h) for h in hotels],
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
        WHERE room_id = $1 AND status IN ('Подтверждено', 'Ожидает оплаты')
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
        VALUES ($1, $2, $3, $4, $5, 'Ожидает оплаты') RETURNING id
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

    from app.auth.flash import flash
    resp = RedirectResponse(url="/portal/tourist/", status_code=303)
    flash(resp, "Спасибо за отзыв!", "success")
    return resp


@router.get("/hotel/{hotel_id}", response_class=HTMLResponse)
async def hotel_detail(
    request: Request,
    hotel_id: int,
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    hotel = await db.fetchrow("""
        SELECT h.*, COALESCE(ROUND(AVG(r.rating), 1), 0) AS avg_rating,
               COUNT(r.id) AS review_count
        FROM hotels h LEFT JOIN reviews r ON r.hotel_id = h.id
        WHERE h.id = $1 GROUP BY h.id
    """, hotel_id)
    if not hotel:
        raise HTTPException(404, "Отель не найден")

    rooms_by_cat = await db.fetch("""
        SELECT rc.id, rc.name, rc.base_price, rc.capacity,
               COUNT(r.id) AS room_count
        FROM room_categories rc
        JOIN rooms r ON r.category_id = rc.id
        WHERE r.hotel_id = $1 AND r.room_condition = 'Исправно'
        GROUP BY rc.id ORDER BY rc.base_price
    """, hotel_id)

    reviews = await db.fetch("""
        SELECT r.rating, r.comment, r.created_at, g.full_name
        FROM reviews r JOIN guests g ON g.id = r.guest_id
        WHERE r.hotel_id = $1 ORDER BY r.created_at DESC LIMIT 10
    """, hotel_id)

    return templates.TemplateResponse("portal/tourist/hotel.html", {
        "request": request, "current_user": user, "user": user,
        "hotel": hotel, "rooms_by_cat": rooms_by_cat, "reviews": reviews,
    })


@router.get("/booking/{booking_id}", response_class=HTMLResponse)
async def booking_detail(
    request: Request,
    booking_id: int,
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    booking = await db.fetchrow("""
        SELECT b.*, h.name AS hotel_name, h.address AS hotel_address,
               r.room_number, rc.name AS category_name, rc.capacity,
               g.full_name
        FROM bookings b
        JOIN rooms r ON r.id = b.room_id
        JOIN hotels h ON h.id = r.hotel_id
        JOIN room_categories rc ON rc.id = r.category_id
        JOIN guests g ON g.id = b.guest_id
        JOIN users u ON u.guest_id = g.id
        WHERE b.id = $1 AND u.id = $2
    """, booking_id, user.id)
    if not booking:
        raise HTTPException(404, "Бронирование не найдено")

    orders = await db.fetch("""
        SELECT so.id, so.quantity, so.ordered_at,
               s.name, s.price, s.is_package
        FROM service_orders so JOIN services s ON s.id = so.service_id
        WHERE so.booking_id = $1 ORDER BY so.ordered_at DESC
    """, booking_id)
    services = await db.fetch(
        "SELECT id, name, price, is_package FROM services ORDER BY is_package DESC, price"
    )
    return templates.TemplateResponse("portal/tourist/booking_detail.html", {
        "request": request, "current_user": user, "user": user,
        "booking": booking, "orders": orders, "services": services,
    })


@router.post("/booking/{booking_id}/service", response_class=HTMLResponse)
async def order_service(
    booking_id: int,
    service_id: int = Form(...),
    quantity: int = Form(1),
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    # verify the booking belongs to this user
    own = await db.fetchval("""
        SELECT 1 FROM bookings b
        JOIN guests g ON g.id = b.guest_id
        JOIN users u ON u.guest_id = g.id
        WHERE b.id = $1 AND u.id = $2
    """, booking_id, user.id)
    if not own:
        raise HTTPException(404, "Бронирование не найдено")

    await db.execute("""
        INSERT INTO service_orders (booking_id, service_id, quantity)
        VALUES ($1, $2, $3)
    """, booking_id, service_id, max(1, quantity))

    from app.auth.flash import flash
    resp = RedirectResponse(url=f"/portal/tourist/booking/{booking_id}", status_code=303)
    flash(resp, "Услуга добавлена к бронированию", "success")
    return resp


@router.post("/booking/{booking_id}/pay")
async def pay_booking(
    booking_id: int,
    request: Request,
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    booking = await db.fetchrow("""
        SELECT b.id, b.total_price, b.payment_status
        FROM bookings b
        JOIN guests g ON g.id = b.guest_id
        JOIN users u ON u.guest_id = g.id
        WHERE b.id = $1 AND u.id = $2
    """, booking_id, user.id)
    if not booking:
        raise HTTPException(404, "Бронирование не найдено")
    if booking["payment_status"] == "Оплачено":
        raise HTTPException(400, "Уже оплачено")

    from app.payments import create_payment
    return_url = str(request.base_url) + f"portal/tourist/payment/callback?booking_id={booking_id}"
    pay_url, payment_id = create_payment(float(booking["total_price"]), booking_id, return_url)
    await db.execute(
        "UPDATE bookings SET yookassa_payment_id = $1 WHERE id = $2",
        payment_id, booking_id
    )
    return RedirectResponse(url=pay_url, status_code=303)

@router.get("/payment/callback")
async def payment_callback(booking_id: int) -> HTMLResponse:
    return RedirectResponse(url=f"/portal/tourist/booking/{booking_id}", status_code=303)


@router.post("/payment/webhook")
async def payment_webhook(
    request: Request,
    db: Database = Depends(get_db),
) -> dict:
    body = await request.json()
    if body.get("event") == "payment.succeeded":
        booking_id = body["object"]["metadata"].get("booking_id")
        if booking_id:
            await db.execute(
                "UPDATE bookings SET payment_status = 'Оплачено', status = 'Подтверждено' WHERE id = $1",
                int(booking_id),
            )
    return {"ok": True}


@router.post("/booking/{booking_id}/cancel", response_class=HTMLResponse)
async def cancel_booking(
    booking_id: int,
    user: CurrentUser = Depends(require_tourist),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    own = await db.fetchrow("""
        SELECT b.id, b.status, b.total_price, g.id AS guest_id FROM bookings b
        JOIN guests g ON g.id = b.guest_id
        JOIN users u ON u.guest_id = g.id
        WHERE b.id = $1 AND u.id = $2
    """, booking_id, user.id)
    
    if not own:
        raise HTTPException(404, "Бронирование не найдено")
    if own["status"] not in ("Подтверждено", "Ожидает оплаты"):
        resp = RedirectResponse(url="/portal/tourist/", status_code=303)
        flash(resp, "Это бронирование нельзя отменить", "warning")
        return resp
    # после проверки статуса добавить разветвление
    if own["status"] == "Ожидает оплаты":
        # денег не было просто отменяем
        await db.execute("UPDATE bookings SET status = 'Отменено' WHERE id = $1", booking_id)
        await db.execute(
            "UPDATE guests SET total_spend = GREATEST(0, total_spend - $1) WHERE id = $2",
            own["total_price"], own["guest_id"],
        )
    else:
        existing_refund = await db.fetchrow(
            "SELECT id FROM refund_requests WHERE booking_id = $1 AND status = 'Новая'",
            booking_id
        )
        if existing_refund:
            resp = RedirectResponse(url="/portal/tourist/", status_code=303)
            flash(resp, "Заявка на возврат уже отправлена", "warning")
            return resp
        # оплачено создаём заявку на возврат
        await db.execute("""
            INSERT INTO refund_requests (booking_id, guest_id, amount)
            VALUES ($1, $2, $3)
        """, booking_id, own["guest_id"], own["total_price"])
        # бронь не отменяем сразу ждём менеджера

    resp = RedirectResponse(url="/portal/tourist/", status_code=303)
    if own["status"] == "Ожидает оплаты":
        flash(resp, "Бронирование отменено", "info")
    else:
        flash(resp, "Заявка на возврат отправлена менеджеру", "info")
    return resp
