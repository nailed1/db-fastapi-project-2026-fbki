"""hotel_utils — pricing, loyalty, and availability utilities for hotel booking systems."""

from hotel_utils.availability import DateRange, is_available, nights_count
from hotel_utils.loyalty import LoyaltyTier, discount_for_tier, tier_from_spend
from hotel_utils.pricing import calculate_price, seasonal_multiplier

__all__ = [
    "DateRange",
    "is_available",
    "nights_count",
    "LoyaltyTier",
    "discount_for_tier",
    "tier_from_spend",
    "calculate_price",
    "seasonal_multiplier",
]

__version__ = "0.1.0"
