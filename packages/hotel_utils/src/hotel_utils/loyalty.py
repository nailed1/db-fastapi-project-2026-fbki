"""Guest loyalty tier logic."""

from decimal import Decimal
from enum import Enum


class LoyaltyTier(str, Enum):
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"


_TIER_THRESHOLDS: list[tuple[Decimal, LoyaltyTier]] = [
    (Decimal("100000"), LoyaltyTier.PLATINUM),
    (Decimal("30000"), LoyaltyTier.GOLD),
    (Decimal("0"), LoyaltyTier.SILVER),
]

_TIER_DISCOUNTS: dict[LoyaltyTier, Decimal] = {
    LoyaltyTier.SILVER: Decimal("0.05"),
    LoyaltyTier.GOLD: Decimal("0.10"),
    LoyaltyTier.PLATINUM: Decimal("0.15"),
}


def tier_from_spend(total_spend: Decimal) -> LoyaltyTier:
    """Return loyalty tier for a guest based on their total historical spend."""
    for threshold, tier in _TIER_THRESHOLDS:
        if total_spend >= threshold:
            return tier
    return LoyaltyTier.SILVER


def discount_for_tier(tier: LoyaltyTier) -> Decimal:
    """Return the fractional discount for a loyalty tier (e.g. 0.10 = 10%)."""
    return _TIER_DISCOUNTS[tier]
