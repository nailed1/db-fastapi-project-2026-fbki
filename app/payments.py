"""ЮKassa payment helpers."""
import uuid
import yookassa
from app.config import settings


def init_yookassa() -> None:
    yookassa.Configuration.account_id = settings.yookassa_shop_id
    yookassa.Configuration.secret_key = settings.yookassa_secret_key


def create_payment(amount: float, booking_id: int, return_url: str) -> str:
    payment = yookassa.Payment.create({
        "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": f"Оплата бронирования №{booking_id}",
        "metadata": {"booking_id": booking_id},
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url