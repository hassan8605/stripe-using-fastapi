"""
subscriptions/service.py
────────────────────────
Recurring billing. Stripe auto-charges customers on schedule.

Dashboard setup before using:
  1. Dashboard → Products → Add Product
  2. Set recurring price (e.g. $9.99/month)
  3. Copy the Price ID (price_xxx)

Subscription lifecycle (via webhooks):
  incomplete → active → past_due → canceled / unpaid
  customer.subscription.* events fire on every state change
  invoice.paid fires on every successful renewal
"""

import stripe
from src.config import stripe  # ensures api_key is set
from src.subscriptions.schema import CreateSubscriptionRequest


def create_subscription(data: CreateSubscriptionRequest) -> stripe.Subscription:
    """
    Steps:
    1. Find or create Customer by email
    2. Create Subscription with default_incomplete status
    3. Return client_secret from latest_invoice so frontend can collect card
    """
    # 1. Find or create customer
    existing = stripe.Customer.list(email=data.customer_email, limit=1).data
    customer = existing[0] if existing else stripe.Customer.create(email=data.customer_email)

    # 2. Create subscription
    return stripe.Subscription.create(
        customer=customer.id,
        items=[{"price": data.price_id}],
        payment_behavior="default_incomplete",
        payment_settings={"save_default_payment_method": "on_subscription"},
        expand=["latest_invoice.payment_intent"],
        metadata=data.metadata or {},
    )


def retrieve_subscription(sub_id: str) -> stripe.Subscription:
    return stripe.Subscription.retrieve(sub_id)


def cancel_subscription(sub_id: str, immediately: bool = True) -> stripe.Subscription:
    """
    immediately=True  → cancel right now (status → canceled)
    immediately=False → cancel at period end (customer keeps access until then)
    """
    if immediately:
        return stripe.Subscription.cancel(sub_id)
    return stripe.Subscription.modify(sub_id, cancel_at_period_end=True)


def list_subscriptions(customer_id: str) -> list:
    return stripe.Subscription.list(customer=customer_id).data
