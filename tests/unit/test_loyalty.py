"""Unit tests for hotel_utils.loyalty."""

from decimal import Decimal

from hotel_utils.loyalty import LoyaltyTier, discount_for_tier, tier_from_spend


def test_tier_silver_low_spend():
    assert tier_from_spend(Decimal("0")) == LoyaltyTier.SILVER


def test_tier_silver_boundary():
    assert tier_from_spend(Decimal("29999")) == LoyaltyTier.SILVER


def test_tier_gold():
    assert tier_from_spend(Decimal("30000")) == LoyaltyTier.GOLD


def test_tier_gold_mid():
    assert tier_from_spend(Decimal("55000")) == LoyaltyTier.GOLD


def test_tier_platinum():
    assert tier_from_spend(Decimal("100000")) == LoyaltyTier.PLATINUM


def test_tier_platinum_high():
    assert tier_from_spend(Decimal("500000")) == LoyaltyTier.PLATINUM


def test_discount_silver():
    assert discount_for_tier(LoyaltyTier.SILVER) == Decimal("0.05")


def test_discount_gold():
    assert discount_for_tier(LoyaltyTier.GOLD) == Decimal("0.10")


def test_discount_platinum():
    assert discount_for_tier(LoyaltyTier.PLATINUM) == Decimal("0.15")
