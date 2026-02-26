"""
customers/service.py
────────────────────
All Stripe Customer API calls. Routers call these functions only.
"""

import stripe
from src.config import stripe  # ensures api_key is set
from src.customers.schema import CreateCustomerRequest


def create_customer(data: CreateCustomerRequest) -> stripe.Customer:
    """
    Creates a Stripe Customer.
    Customers let you: save payment methods, attach subscriptions, track charges.
    """
    return stripe.Customer.create(
        email=data.email,
        name=data.name,
        phone=data.phone,
        metadata=data.metadata or {},
    )


def get_customer(customer_id: str) -> stripe.Customer:
    return stripe.Customer.retrieve(customer_id)


def list_customers(limit: int = 10) -> list:
    return stripe.Customer.list(limit=limit).data


def delete_customer(customer_id: str) -> dict:
    return stripe.Customer.delete(customer_id)


def list_payment_methods(customer_id: str, pm_type: str = "card") -> list:
    """List saved payment methods for a customer (e.g. saved cards)."""
    return stripe.PaymentMethod.list(customer=customer_id, type=pm_type).data


def detach_payment_method(payment_method_id: str) -> stripe.PaymentMethod:
    """Remove a saved card from a customer."""
    return stripe.PaymentMethod.detach(payment_method_id)
