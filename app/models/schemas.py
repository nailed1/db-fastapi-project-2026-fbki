"""Pydantic schemas for request / response validation."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, field_validator


# Hotels

class HotelOut(BaseModel):
    id: int
    name: str
    address: str
    director_name: str
    overbooking_limit: int


# Room categories

class RoomCategoryOut(BaseModel):
    id: int
    name: str
    base_price: Decimal
    capacity: int


# Rooms

class RoomOut(BaseModel):
    id: int
    hotel_id: int
    category_id: int
    room_number: int
    cleaning_status: str
    room_condition: str
    category_name: str | None = None
    base_price: Decimal | None = None


# Guests

class GuestCreate(BaseModel):
    full_name: str
    passport: str
    phone: str | None = None
    email: EmailStr | None = None

    @field_validator("passport")
    @classmethod
    def passport_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("passport cannot be empty")
        return v.strip()


class GuestOut(BaseModel):
    id: int
    full_name: str
    passport: str
    phone: str | None
    email: str | None
    loyalty_tier: str
    total_spend: Decimal


# Bookings

class BookingCreate(BaseModel):
    guest_id: int
    room_id: int
    check_in: date
    check_out: date

    @field_validator("check_out")
    @classmethod
    def check_out_after_check_in(cls, v: date, info: object) -> date:
        data = getattr(info, "data", {})
        if "check_in" in data and v <= data["check_in"]:
            raise ValueError("check_out must be after check_in")
        return v


class BookingOut(BaseModel):
    id: int
    guest_id: int
    room_id: int
    check_in: date
    check_out: date
    total_price: Decimal
    status: str
    guest_name: str | None = None
    room_number: int | None = None
    hotel_name: str | None = None


# Services

class ServiceOut(BaseModel):
    id: int
    name: str
    price: Decimal
    is_package: bool


class ServiceOrderCreate(BaseModel):
    booking_id: int
    service_id: int
    quantity: int = 1


# Staff

class StaffOut(BaseModel):
    id: int
    hotel_id: int
    full_name: str
    role: str
    login: str
