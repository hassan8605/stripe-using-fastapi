"""
webhooks/service.py
───────────────────
Webhook signature verification.
NEVER process a webhook without verifying the signature first.
"""

import stripe
from src.config import stripe  # ensures api_key is set
from src.settings import settings


def verify_and_construct_event(payload: bytes, signature: str) -> stripe.Event:
    """
    Verify that the request is genuinely from Stripe using HMAC signature.
    Raises stripe.error.SignatureVerificationError if invalid.
    """
    return stripe.Webhook.construct_event(
        payload, signature, settings.STRIPE_WEBHOOK_SECRET
    )
