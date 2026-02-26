"""
src/models.py
─────────────
Shared enums and constants used across Stripe modules.
In a DB-backed project this would contain SQLAlchemy models.
"""

from enum import Enum


class Currency(str, Enum):
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    PKR = "pkr"
    AED = "aed"


class PaymentIntentStatus(str, Enum):
    REQUIRES_PAYMENT_METHOD = "requires_payment_method"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_ACTION = "requires_action"
    PROCESSING = "processing"
    REQUIRES_CAPTURE = "requires_capture"
    CANCELED = "canceled"
    SUCCEEDED = "succeeded"


class SubscriptionStatus(str, Enum):
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class RefundReason(str, Enum):
    DUPLICATE = "duplicate"
    FRAUDULENT = "fraudulent"
    REQUESTED_BY_CUSTOMER = "requested_by_customer"


class WebhookEventType(str, Enum):
    PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
    PAYMENT_INTENT_FAILED = "payment_intent.payment_failed"
    PAYMENT_INTENT_CANCELED = "payment_intent.canceled"
    CHECKOUT_COMPLETED = "checkout.session.completed"
    CHECKOUT_EXPIRED = "checkout.session.expired"
    SUBSCRIPTION_CREATED = "customer.subscription.created"
    SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    INVOICE_UPCOMING = "invoice.upcoming"
