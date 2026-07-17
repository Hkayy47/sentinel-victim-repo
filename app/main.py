"""FastAPI entrypoint for the demo pricing service."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app.pricing import LineItem, order_total_cents

app = FastAPI(title="Sentinel Demo Pricing Service")


class LineItemIn(BaseModel):
    """Request-body shape for a single line item."""

    name: str
    unit_price_cents: int
    quantity: int


class OrderRequest(BaseModel):
    """Request-body shape for an order pricing request."""

    items: list[LineItemIn]
    discount_percent: float = 0.0
    tax_rate_percent: float = 0.0


@app.post("/order/total")
def order_total(request: OrderRequest) -> dict[str, int]:
    """Compute the total price of an order.

    Args:
        request: The order's line items, discount, and tax rate.

    Returns:
        A JSON-serializable dict with the final total in cents.
    """
    items = [
        LineItem(
            name=item.name,
            unit_price_cents=item.unit_price_cents,
            quantity=item.quantity,
        )
        for item in request.items
    ]
    total = order_total_cents(
        items,
        discount_percent=request.discount_percent,
        tax_rate_percent=request.tax_rate_percent,
    )
    return {"total_cents": total}


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check endpoint.

    Returns:
        A dict indicating the service is up.
    """
    return {"status": "ok"}
