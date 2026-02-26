"""
checkout/service.py
───────────────────
Stripe-hosted payment page — easiest integration path.

User flow:
  1. Create session → get URL
  2. Redirect user to URL (Stripe's page)
  3. User pays → Stripe redirects to success_url or cancel_url
  4. Verify via webhook: checkout.session.completed

Advantages over PaymentIntents:
  - Zero frontend work (no Stripe.js / Elements needed)
  - Handles SCA / 3DS automatically
  - Supports Apple Pay, Google Pay out of the box
  - Stripe handles PCI compliance entirely
"""

import stripe
from src.config import stripe  # ensures api_key is set
from src.checkout.schema import CreateCheckoutSessionRequest
from src.settings import settings


def create_checkout_session(data: CreateCheckoutSessionRequest) -> stripe.checkout.Session:
    line_items = [
        {
            "price_data": {
                "currency": item.currency,
                "product_data": {"name": item.name},
                "unit_amount": item.amount,
            },
            "quantity": item.quantity,
        }
        for item in data.line_items
    ]

    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        customer_email=data.customer_email,
        success_url=data.success_url or f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=data.cancel_url or f"{settings.FRONTEND_URL}/cancel",
        metadata=data.metadata or {},
    )


def retrieve_checkout_session(session_id: str) -> stripe.checkout.Session:
    return stripe.checkout.Session.retrieve(session_id)
