"""Unit tests for hotel_utils.availability."""

from datetime import date

import pytest

from hotel_utils.availability import DateRange, is_available, nights_count


def make(ci: str, co: str) -> DateRange:
    return DateRange(date.fromisoformat(ci), date.fromisoformat(co))


def test_nights_count():
    assert nights_count(date(2025, 5, 1), date(2025, 5, 5)) == 4


def test_nights_count_invalid():
    with pytest.raises(ValueError):
        nights_count(date(2025, 5, 5), date(2025, 5, 1))


def test_date_range_invalid():
    with pytest.raises(ValueError):
        DateRange(date(2025, 5, 5), date(2025, 5, 3))


def test_no_overlap_before():
    a = make("2025-05-01", "2025-05-05")
    b = make("2025-05-06", "2025-05-10")
    assert not a.overlaps(b)


def test_no_overlap_after():
    a = make("2025-05-10", "2025-05-15")
    b = make("2025-05-01", "2025-05-10")  # ends exactly when a starts
    assert not a.overlaps(b)


def test_overlap_partial():
    a = make("2025-05-03", "2025-05-08")
    b = make("2025-05-06", "2025-05-12")
    assert a.overlaps(b)


def test_overlap_contained():
    a = make("2025-05-01", "2025-05-15")
    b = make("2025-05-05", "2025-05-10")
    assert a.overlaps(b)


def test_is_available_no_bookings():
    requested = make("2025-08-01", "2025-08-05")
    assert is_available(requested, [])


def test_is_available_no_conflict():
    requested = make("2025-08-10", "2025-08-15")
    existing = [make("2025-08-01", "2025-08-10")]
    assert is_available(requested, existing)


def test_is_not_available_conflict():
    requested = make("2025-08-05", "2025-08-12")
    existing = [make("2025-08-08", "2025-08-15")]
    assert not is_available(requested, existing)
