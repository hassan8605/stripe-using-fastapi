"""
refunds/service.py
──────────────────
Refund a PaymentIntent — fully or partially.

Notes:
- Refunds take 5–10 business days to appear on statement
- You can only refund up to the original charged amount
- Partial refunds: pass amount in cents (e.g. 500 = $5.00)
- Reasons: duplicate | fraudulent | requested_by_customer
- Stripe's processing fee is NOT refunded back to you
"""

import stripe
from src.config import stripe  # ensures api_key is set
from src.refunds.schema import CreateRefundRequest


def create_refund(data: CreateRefundRequest) -> stripe.Refund:
    """
    Called by router.py:
        r = service.create_refund(data)
        RefundResponse(refund_id=r.id, amount=r.amount, currency=r.currency, status=r.status)

    Builds params conditionally:
    - payment_intent is always required
    - amount only added for partial refunds (omit = full refund)
    - reason only added if provided
    """
    params: dict = {"payment_intent": data.payment_intent_id}

    if data.amount:
        params["amount"] = data.amount

    if data.reason:
        params["reason"] = data.reason.value  # enum → string e.g. "requested_by_customer"

    return stripe.Refund.create(**params)