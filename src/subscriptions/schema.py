from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class CreateSubscriptionRequest(BaseModel):
    """
    Request body for POST /subscriptions/
    Matches all fields accessed in service.create_subscription():
    - data.customer_email → used to find/create Stripe Customer
    - data.price_id       → passed as items[0].price to Stripe
    - data.metadata       → attached to the Subscription object
    """
    customer_email: EmailStr = Field(..., description="Customer email. Used to find existing or create new Stripe Customer.")
    price_id: str = Field(..., description="Stripe Price ID (price_xxx). Create in Dashboard → Products → Add Price.")
    metadata: Optional[dict] = Field(default=None, description="Key-value pairs attached to the subscription")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_email": "user@example.com",
                "price_id": "price_1OxxxxxxxxxxxxxxxxxxxxXx",
                "metadata": {"user_id": "42", "plan": "pro"}
            }
        }


class SubscriptionResponse(BaseModel):
    """
    Imported in router.py but responses are returned as raw dicts.
    Kept here for future use or if you switch to response_model on the POST endpoint.

    Fields match exactly what router.py returns:
    - subscription_id        → sub.id
    - customer_id            → sub.customer
    - status                 → sub.status
    - current_period_end     → sub.current_period_end (Unix timestamp)
    - client_secret          → sub.latest_invoice.payment_intent.client_secret (can be None)
    """
    subscription_id: str = Field(..., description="Stripe Subscription ID (sub_xxx)")
    customer_id: str = Field(..., description="Stripe Customer ID (cus_xxx)")
    status: str = Field(..., description="Subscription status: incomplete | active | past_due | canceled")
    current_period_end: int = Field(..., description="Unix timestamp of when the current billing period ends")
    client_secret: Optional[str] = Field(
        default=None,
        description="Pass to stripe.confirmCardPayment() on frontend to collect first payment. None if already active."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "subscription_id": "sub_1OxxxxxxxxxxxxxxxxxxxxXx",
                "customer_id": "cus_xxxxxxxxxxxxxxxx",
                "status": "incomplete",
                "current_period_end": 1735689600,
                "client_secret": "pi_3OxxxxxxxxxxxxxxxxxxxxXx_secret_xxxxxxxx"
            }
        }