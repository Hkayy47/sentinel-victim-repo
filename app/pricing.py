"""Order pricing logic for the demo service.

This module is intentionally small and dependency-free so that CI runs
fast and any bug Sentinel needs to diagnose is easy to reason about from
a stack trace alone.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LineItem:
    """A single item in an order.

    Args:
        name: Human-readable item name.
        unit_price_cents: Price of one unit, in integer cents.
        quantity: Number of units purchased.
    """

    name: str
    unit_price_cents: int
    quantity: int


def line_item_total(item: LineItem) -> int:
    """Compute the total cost of a single line item in cents.

    Args:
        item: The line item to price.

    Returns:
        Total price in integer cents (unit price times quantity).
    """
    return item.unit_price_cents * item.quantity


def subtotal_cents(items: list[LineItem]) -> int:
    """Sum the totals of every line item in an order.

    Args:
        items: All line items in the order.

    Returns:
        Order subtotal in integer cents, before tax and discount.
    """
    return sum(line_item_total(item) for item in items)


def apply_discount(subtotal: int, discount_percent: float) -> int:
    """Apply a percentage discount to a subtotal.

    Args:
        subtotal: Pre-discount amount in integer cents.
        discount_percent: Discount to apply, expressed 0-100.

    Returns:
        Discounted amount in integer cents, rounded to the nearest cent.
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    kept_fraction = (100 - discount_percent) / 100
    return round(subtotal * kept_fraction)


def apply_tax(amount_cents: int, tax_rate_percent: float) -> int:
    """Apply a percentage tax rate on top of an amount.

    Args:
        amount_cents: Pre-tax amount in integer cents.
        tax_rate_percent: Tax rate to apply, expressed 0-100.

    Returns:
        Amount including tax, in integer cents, rounded to the nearest cent.
    """
    if tax_rate_percent < 0:
        raise ValueError("tax_rate_percent must be non-negative")
    return round(amount_cents * (1 + tax_rate_percent / 100))


def order_total_cents(
    items: list[LineItem],
    discount_percent: float = 0.0,
    tax_rate_percent: float = 0.0,
) -> int:
    """Compute the final total for an order: subtotal, discount, then tax.

    Args:
        items: All line items in the order.
        discount_percent: Discount to apply to the subtotal, 0-100.
        tax_rate_percent: Tax rate to apply after discount, 0-100.

    Returns:
        Final order total in integer cents.
    """
    subtotal = subtotal_cents(items)
    discounted = apply_discount(subtotal, discount_percent)
    return discounted
