# hotel-utils

Utility library for hotel booking systems: dynamic pricing, loyalty tiers, and availability checks.

## Installation

```bash
pip install -i https://test.pypi.org/simple/ hotel-utils
```

## Usage

```python
from datetime import date
from decimal import Decimal
from hotel_utils import calculate_price, tier_from_spend, discount_for_tier, is_available, DateRange

# Dynamic pricing
price = calculate_price(
    base_price=Decimal("3000"),
    check_in=date(2025, 7, 10),
    check_out=date(2025, 7, 15),
    loyalty_discount=Decimal("0.10"),
)
print(price)  # 3000 * 1.30 * 5 nights * 0.90 = 17550.00

# Loyalty tier
tier = tier_from_spend(Decimal("45000"))  # LoyaltyTier.GOLD
discount = discount_for_tier(tier)        # Decimal("0.10")

# Availability
requested = DateRange(date(2025, 8, 1), date(2025, 8, 5))
existing = [DateRange(date(2025, 8, 3), date(2025, 8, 8))]
print(is_available(requested, existing))  # False
```

## License

MIT
