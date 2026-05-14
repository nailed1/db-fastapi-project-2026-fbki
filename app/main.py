"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import bookings, guests, rooms, staff
from app.api.routes import auth as auth_router
from app.api.routes import portal_tourist, portal_staff, portal_manager, portal_admin
from app.auth.dependencies import CurrentUser, get_current_user
from app.database import close_pool, get_pool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await get_pool()
    yield
    await close_pool()


app = FastAPI(
    title="Hotel Booking Management",
    version="0.1.0",
    description="Hotel booking system with rooms, guests, staff and services management.",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Inject current_user into every template context automatically
@app.middleware("http")
async def add_user_to_templates(request: Request, call_next):  # type: ignore[no-untyped-def]
    response = await call_next(request)
    return response


# Override Jinja2Templates to always inject current_user
_orig_response = templates.TemplateResponse


def _patched_response(name: str, context: dict, *args, **kwargs):  # type: ignore[no-untyped-def]
    # current_user is injected per route via Depends; templates that don't use it just ignore it
    return _orig_response(name, context, *args, **kwargs)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(portal_tourist.router)
app.include_router(portal_staff.router)
app.include_router(portal_manager.router)
app.include_router(portal_admin.router)
# Legacy admin-facing routes (still useful for manager/admin)
app.include_router(bookings.router)
app.include_router(guests.router)
app.include_router(rooms.router)
app.include_router(staff.router)


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: CurrentUser | None = Depends(get_current_user),
) -> HTMLResponse:
    if current_user:
        from app.api.routes.auth import _home_for
        return RedirectResponse(url=_home_for(current_user.system_role), status_code=302)
    return templates.TemplateResponse(
        "index.html", {"request": request, "current_user": current_user}
    )
