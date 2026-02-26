"""
payment_intents/service.py
──────────────────────────
PaymentIntent lifecycle: create → confirm → cancel → retrieve → list

PaymentIntent is the CORE object in modern Stripe.
It tracks the full lifecycle of collecting a payment.

Lifecycle states:
  requires_payment_method → requires_confirmation → requires_action
  → processing → succeeded | canceled
"""

import stripe
from src.config import stripe  # ensures api_key is set
from src.payment_intents.schema import CreatePaymentIntentRequest


def create_payment_intent(data: CreatePaymentIntentRequest) -> stripe.PaymentIntent:
    """
    Creates a PaymentIntent.
    Returns a client_secret → send to frontend → Stripe.js confirms it.
    automatic_payment_methods lets Stripe enable cards, wallets, etc. automatically.
    """
    params = {
        "amount": data.amount,
        "currency": data.currency,
        "automatic_payment_methods": {"enabled": True},
    }
    if data.description:
        params["description"] = data.description
    if data.customer_id:
        params["customer"] = data.customer_id
    if data.metadata:
        params["metadata"] = data.metadata

    return stripe.PaymentIntent.create(**params)


def retrieve_payment_intent(pi_id: str) -> stripe.PaymentIntent:
    return stripe.PaymentIntent.retrieve(pi_id)


def confirm_payment_intent(pi_id: str, payment_method: str = "pm_card_visa") -> stripe.PaymentIntent:
    """
    Server-side confirm (test/server flows only).
    In production the FRONTEND confirms using stripe.confirmCardPayment(client_secret).
    """
    return stripe.PaymentIntent.confirm(pi_id, payment_method=payment_method)


def cancel_payment_intent(pi_id: str) -> stripe.PaymentIntent:
    """
    Cancel before it's confirmed. Releases held funds.
    Cannot cancel after status=processing.
    """
    return stripe.PaymentIntent.cancel(pi_id)


def list_payment_intents(limit: int = 10) -> list:
    return stripe.PaymentIntent.list(limit=limit).data
