"""Rooms routes — list and cleaning status update."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import get_db
from app.database import Database

router = APIRouter(prefix="/rooms", tags=["rooms"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_rooms(request: Request, db: Database = Depends(get_db)) -> HTMLResponse:
    rows = await db.fetch("""
        SELECT r.id, r.room_number, r.cleaning_status, r.room_condition,
               rc.name AS category_name, rc.base_price,
               h.name AS hotel_name
        FROM rooms r
        JOIN room_categories rc ON rc.id = r.category_id
        JOIN hotels h ON h.id = r.hotel_id
        ORDER BY h.name, r.room_number
    """)
    return templates.TemplateResponse(
        "rooms/list.html", {"request": request, "rooms": rows}
    )


@router.post("/{room_id}/cleaning", response_class=HTMLResponse)
async def update_cleaning(
    room_id: int,
    status: str = Form(...),
    db: Database = Depends(get_db),
) -> HTMLResponse:
    valid = {"Clean", "Dirty", "Cleaning"}
    if status not in valid:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from {valid}")
    await db.execute(
        "UPDATE rooms SET cleaning_status = $1 WHERE id = $2", status, room_id
    )
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/rooms/", status_code=303)
