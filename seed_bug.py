#!/usr/bin/env python3
"""Seed a deterministic bug into app/pricing.py for the Sentinel demo.

Usage:
    python seed_bug.py easy      # one-line arithmetic typo
    python seed_bug.py medium    # discount/tax applied in the wrong order
    python seed_bug.py hard      # bug lives in a different function than
                                  # the one the failing test output suggests
    python seed_bug.py revert    # restore the original, working file

Each bug is applied as an exact string replacement against the known-good
source, so this script is idempotent and safe to run repeatedly during a
live demo.
"""

from __future__ import annotations

import sys
from pathlib import Path

PRICING_PATH = Path(__file__).parent / "app" / "pricing.py"

ORIGINAL_DISCOUNT = """def apply_discount(subtotal: int, discount_percent: float) -> int:
    \"\"\"Apply a percentage discount to a subtotal.

    Args:
        subtotal: Pre-discount amount in integer cents.
        discount_percent: Discount to apply, expressed 0-100.

    Returns:
        Discounted amount in integer cents, rounded to the nearest cent.
    \"\"\"
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    kept_fraction = (100 - discount_percent) / 100
    return round(subtotal * kept_fraction)"""

EASY_BUG_DISCOUNT = """def apply_discount(subtotal: int, discount_percent: float) -> int:
    \"\"\"Apply a percentage discount to a subtotal.

    Args:
        subtotal: Pre-discount amount in integer cents.
        discount_percent: Discount to apply, expressed 0-100.

    Returns:
        Discounted amount in integer cents, rounded to the nearest cent.
    \"\"\"
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    kept_fraction = (100 - discount_percent) / 1000
    return round(subtotal * kept_fraction)"""

ORIGINAL_ORDER_TOTAL = """def order_total_cents(
    items: list[LineItem],
    discount_percent: float = 0.0,
    tax_rate_percent: float = 0.0,
) -> int:
    \"\"\"Compute the final total for an order: subtotal, discount, then tax.

    Args:
        items: All line items in the order.
        discount_percent: Discount to apply to the subtotal, 0-100.
        tax_rate_percent: Tax rate to apply after discount, 0-100.

    Returns:
        Final order total in integer cents.
    \"\"\"
    subtotal = subtotal_cents(items)
    discounted = apply_discount(subtotal, discount_percent)
    return apply_tax(discounted, tax_rate_percent)"""

MEDIUM_BUG_ORDER_TOTAL = """def order_total_cents(
    items: list[LineItem],
    discount_percent: float = 0.0,
    tax_rate_percent: float = 0.0,
) -> int:
    \"\"\"Compute the final total for an order: subtotal, discount, then tax.

    Args:
        items: All line items in the order.
        discount_percent: Discount to apply to the subtotal, 0-100.
        tax_rate_percent: Tax rate to apply after discount, 0-100.

    Returns:
        Final order total in integer cents.
    \"\"\"
    subtotal = subtotal_cents(items)
    discounted = apply_discount(subtotal, discount_percent)
    return discounted"""

ORIGINAL_LINE_ITEM_TOTAL = """def line_item_total(item: LineItem) -> int:
    \"\"\"Compute the total cost of a single line item in cents.

    Args:
        item: The line item to price.

    Returns:
        Total price in integer cents (unit price times quantity).
    \"\"\"
    return item.unit_price_cents * item.quantity"""

HARD_BUG_LINE_ITEM_TOTAL = """def line_item_total(item: LineItem) -> int:
    \"\"\"Compute the total cost of a single line item in cents.

    Args:
        item: The line item to price.

    Returns:
        Total price in integer cents (unit price times quantity).
    \"\"\"
    return item.unit_price_cents * item.quantity if item.quantity <= 1 else item.unit_price_cents + item.quantity"""

BUGS: dict[str, tuple[str, str]] = {
    "easy": (ORIGINAL_DISCOUNT, EASY_BUG_DISCOUNT),
    "medium": (ORIGINAL_ORDER_TOTAL, MEDIUM_BUG_ORDER_TOTAL),
    # The hard bug's failing test is test_order_total_with_discount_and_tax,
    # which touches apply_discount and apply_tax in its traceback context —
    # but the actual defect is in line_item_total, one function away from
    # where the obvious first fix would look.
    "hard": (ORIGINAL_LINE_ITEM_TOTAL, HARD_BUG_LINE_ITEM_TOTAL),
}


def seed(level: str) -> None:
    """Inject the named bug into app/pricing.py.

    Args:
        level: One of "easy", "medium", "hard", or "revert".
    """
    source = PRICING_PATH.read_text()

    if level == "revert":
        for original, broken in BUGS.values():
            source = source.replace(broken, original)
        PRICING_PATH.write_text(source)
        print("Reverted app/pricing.py to the original, working version.")
        return

    if level not in BUGS:
        raise SystemExit(f"Unknown bug level '{level}'. Choose from: easy, medium, hard, revert.")

    original, broken = BUGS[level]
    if broken in source:
        print(f"Bug '{level}' is already seeded. No changes made.")
        return
    if original not in source:
        raise SystemExit(
            f"Could not find the expected original code for bug '{level}'. "
            "The file may already have a different bug seeded — run "
            "'python seed_bug.py revert' first."
        )

    source = source.replace(original, broken)
    PRICING_PATH.write_text(source)
    print(f"Seeded '{level}' bug into app/pricing.py.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    seed(sys.argv[1])
