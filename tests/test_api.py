"""API-level tests for the FastAPI app."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_order_total_endpoint() -> None:
    payload = {
        "items": [{"name": "Widget", "unit_price_cents": 500, "quantity": 2}],
        "discount_percent": 0,
        "tax_rate_percent": 0,
    }
    response = client.post("/order/total", json=payload)
    assert response.status_code == 200
    assert response.json() == {"total_cents": 1000}


def test_order_total_endpoint_with_discount() -> None:
    payload = {
        "items": [{"name": "Widget", "unit_price_cents": 1000, "quantity": 1}],
        "discount_percent": 20,
        "tax_rate_percent": 10,
    }
    response = client.post("/order/total", json=payload)
    assert response.status_code == 200
    assert response.json() == {"total_cents": 880}
