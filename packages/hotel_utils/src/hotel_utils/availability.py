"""Date range utilities for availability checks."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DateRange:
    check_in: date
    check_out: date

    def __post_init__(self) -> None:
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")

    def overlaps(self, other: "DateRange") -> bool:
        """Return True if this range overlaps with another."""
        return self.check_in < other.check_out and other.check_in < self.check_out


def nights_count(check_in: date, check_out: date) -> int:
    """Return the number of nights between two dates."""
    delta = (check_out - check_in).days
    if delta <= 0:
        raise ValueError("check_out must be after check_in")
    return delta


def is_available(requested: DateRange, existing_bookings: list[DateRange]) -> bool:
    """Return True if the requested range does not overlap any existing booking."""
    return not any(requested.overlaps(b) for b in existing_bookings)
