"""
tests/test_payments.py
─────────────────────
Run: pytest tests/ -v
Uses mocks — no real Stripe charges.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


# ── Payment Intents ────────────────────────────────────────────────────────────

@patch("src.payment_intents.service.stripe.PaymentIntent.create")
def test_create_payment_intent(mock_create):
    pi = MagicMock()
    pi.id = "pi_test_123"
    pi.client_secret = "pi_test_123_secret"
    pi.amount = 2000
    pi.currency = "usd"
    pi.status = "requires_payment_method"
    pi.description = None
    mock_create.return_value = pi

    r = client.post("/api/v1/payment-intents/", json={"amount": 2000, "currency": "usd"})
    assert r.status_code == 200
    assert r.json()["amount"] == 2000
    assert "client_secret" in r.json()


def test_create_payment_intent_invalid_amount():
    r = client.post("/api/v1/payment-intents/", json={"amount": -1, "currency": "usd"})
    assert r.status_code == 422


# ── Customers ─────────────────────────────────────────────────────────────────

@patch("src.customers.service.stripe.Customer.create")
def test_create_customer(mock_create):
    c = MagicMock()
    c.id = "cus_test_123"
    c.email = "test@example.com"
    c.name = "Test User"
    c.created = 1700000000
    mock_create.return_value = c

    r = client.post("/api/v1/customers/", json={"email": "test@example.com", "name": "Test User"})
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"
    assert "customer_id" in r.json()


# ── Checkout ──────────────────────────────────────────────────────────────────

@patch("src.checkout.service.stripe.checkout.Session.create")
def test_create_checkout_session(mock_create):
    session = MagicMock()
    session.id = "cs_test_123"
    session.url = "https://checkout.stripe.com/pay/cs_test_123"
    mock_create.return_value = session

    r = client.post("/api/v1/checkout/", json={
        "line_items": [{"name": "Pro Plan", "amount": 4999, "quantity": 1}],
        "customer_email": "test@example.com"
    })
    assert r.status_code == 200
    assert "url" in r.json()


# ── Refunds ───────────────────────────────────────────────────────────────────

@patch("src.refunds.service.stripe.Refund.create")
def test_create_refund(mock_create):
    refund = MagicMock()
    refund.id = "re_test_123"
    refund.amount = 2000
    refund.currency = "usd"
    refund.status = "succeeded"
    mock_create.return_value = refund

    r = client.post("/api/v1/refunds/", json={
        "payment_intent_id": "pi_test_123",
        "reason": "requested_by_customer"
    })
    assert r.status_code == 200
    assert r.json()["status"] == "succeeded"
