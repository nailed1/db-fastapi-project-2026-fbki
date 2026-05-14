"""Dynamic pricing calculations for hotel rooms."""

from datetime import date
from decimal import Decimal


# Peak months: June–August, December
_PEAK_MONTHS = {6, 7, 8, 12}
_SHOULDER_MONTHS = {3, 4, 5, 9, 10, 11}


def seasonal_multiplier(check_in: date) -> Decimal:
    """Return a price multiplier based on the check-in month.

    Peak season (Jun–Aug, Dec) → 1.30
    Shoulder season (Mar–May, Sep–Nov) → 1.00
    Low season (Jan, Feb) → 0.85
    """
    if check_in.month in _PEAK_MONTHS:
        return Decimal("1.30")
    if check_in.month in _SHOULDER_MONTHS:
        return Decimal("1.00")
    return Decimal("0.85")


def calculate_price(
    base_price: Decimal,
    check_in: date,
    check_out: date,
    loyalty_discount: Decimal = Decimal("0"),
    extra_services: Decimal = Decimal("0"),
) -> Decimal:
    """Calculate the total booking price.

    Args:
        base_price: Nightly price for the room category.
        check_in: Arrival date.
        check_out: Departure date.
        loyalty_discount: Fractional discount, e.g. Decimal("0.10") for 10%.
        extra_services: Fixed amount for ordered services.

    Returns:
        Rounded total in 2 decimal places.

    Raises:
        ValueError: If check_out is not after check_in.
    """
    nights = (check_out - check_in).days
    if nights <= 0:
        raise ValueError("check_out must be after check_in")

    multiplier = seasonal_multiplier(check_in)
    room_total = base_price * multiplier * nights
    discount_amount = room_total * loyalty_discount
    total = room_total - discount_amount + extra_services
    return total.quantize(Decimal("0.01"))
