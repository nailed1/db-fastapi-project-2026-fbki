"""ЮKassa payment helpers."""
import uuid
import yookassa
from app.config import settings


def _has_yookassa_creds() -> bool:
    return bool(settings.yookassa_shop_id and settings.yookassa_secret_key)


def init_yookassa() -> None:
    if _has_yookassa_creds():
        yookassa.Configuration.account_id = settings.yookassa_shop_id
        yookassa.Configuration.secret_key = settings.yookassa_secret_key


def create_payment(amount: float, booking_id: int, return_url: str) -> tuple[str, str]:
    if not _has_yookassa_creds():
        mock_id = f"mock-{uuid.uuid4()}"
        mock_url = f"/portal/tourist/payment/mock?booking_id={booking_id}&payment_id={mock_id}"
        return mock_url, mock_id

    payment = yookassa.Payment.create({
        "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": f"Оплата бронирования №{booking_id}",
        "metadata": {"booking_id": booking_id},
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url, payment.id

def create_refund(payment_id: str, amount: float) -> None:
    import uuid
    yookassa.Refund.create({
        "payment_id": payment_id,
        "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
    }, uuid.uuid4())