"""Tests for app.pricing. Sentinel's job is to keep these green."""

from __future__ import annotations

import pytest

from app.pricing import LineItem, apply_discount, apply_tax, order_total_cents, subtotal_cents


def test_subtotal_single_item() -> None:
    items = [LineItem(name="Widget", unit_price_cents=500, quantity=3)]
    assert subtotal_cents(items) == 1500


def test_subtotal_multiple_items() -> None:
    items = [
        LineItem(name="Widget", unit_price_cents=500, quantity=2),
        LineItem(name="Gadget", unit_price_cents=1000, quantity=1),
    ]
    assert subtotal_cents(items) == 2000


def test_apply_discount_zero() -> None:
    assert apply_discount(1000, 0) == 1000


def test_apply_discount_half() -> None:
    assert apply_discount(1000, 50) == 500


def test_apply_discount_full() -> None:
    assert apply_discount(1000, 100) == 0


def test_apply_discount_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        apply_discount(1000, 150)


def test_apply_tax_zero() -> None:
    assert apply_tax(1000, 0) == 1000


def test_apply_tax_standard_rate() -> None:
    assert apply_tax(1000, 8) == 1080


def test_apply_tax_rejects_negative() -> None:
    with pytest.raises(ValueError):
        apply_tax(1000, -5)


def test_order_total_no_discount_no_tax() -> None:
    items = [LineItem(name="Widget", unit_price_cents=500, quantity=2)]
    assert order_total_cents(items) == 1000


def test_order_total_with_discount_and_tax() -> None:
    items = [LineItem(name="Widget", unit_price_cents=1000, quantity=1)]
    # 1000 -> 20% off -> 800 -> +10% tax -> 880
    assert order_total_cents(items, discount_percent=20, tax_rate_percent=10) == 880


def test_order_total_empty_order() -> None:
    assert order_total_cents([]) == 0
