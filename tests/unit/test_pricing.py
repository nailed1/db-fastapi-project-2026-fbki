"""Unit tests for hotel_utils.pricing."""

from datetime import date
from decimal import Decimal

import pytest

from hotel_utils.pricing import calculate_price, seasonal_multiplier


def test_seasonal_multiplier_peak():
    assert seasonal_multiplier(date(2025, 7, 15)) == Decimal("1.30")


def test_seasonal_multiplier_peak_december():
    assert seasonal_multiplier(date(2025, 12, 25)) == Decimal("1.30")


def test_seasonal_multiplier_shoulder():
    assert seasonal_multiplier(date(2025, 5, 1)) == Decimal("1.00")


def test_seasonal_multiplier_low():
    assert seasonal_multiplier(date(2025, 1, 10)) == Decimal("0.85")


def test_calculate_price_basic():
    price = calculate_price(
        base_price=Decimal("3500"),
        check_in=date(2025, 5, 1),   # shoulder → 1.00
        check_out=date(2025, 5, 5),  # 4 nights
    )
    assert price == Decimal("14000.00")


def test_calculate_price_with_loyalty_discount():
    price = calculate_price(
        base_price=Decimal("3500"),
        check_in=date(2025, 5, 1),
        check_out=date(2025, 5, 5),
        loyalty_discount=Decimal("0.10"),
    )
    assert price == Decimal("12600.00")


def test_calculate_price_peak_season():
    price = calculate_price(
        base_price=Decimal("3000"),
        check_in=date(2025, 7, 10),
        check_out=date(2025, 7, 15),  # 5 nights, 1.30 multiplier
    )
    assert price == Decimal("19500.00")


def test_calculate_price_with_services():
    price = calculate_price(
        base_price=Decimal("3500"),
        check_in=date(2025, 5, 1),
        check_out=date(2025, 5, 3),  # 2 nights
        extra_services=Decimal("1500"),
    )
    assert price == Decimal("8500.00")


def test_calculate_price_invalid_dates():
    with pytest.raises(ValueError, match="check_out must be after check_in"):
        calculate_price(
            base_price=Decimal("3500"),
            check_in=date(2025, 5, 5),
            check_out=date(2025, 5, 1),
        )


def test_calculate_price_same_day():
    with pytest.raises(ValueError):
        calculate_price(
            base_price=Decimal("3500"),
            check_in=date(2025, 5, 5),
            check_out=date(2025, 5, 5),
        )
