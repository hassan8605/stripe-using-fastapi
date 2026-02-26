from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RefundReason(str, Enum):
    """
    Stripe-accepted reason values for a refund.
    Passed as reason= to stripe.Refund.create()
    """
    DUPLICATE = "duplicate"
    FRAUDULENT = "fraudulent"
    REQUESTED_BY_CUSTOMER = "requested_by_customer"


class CreateRefundRequest(BaseModel):
    """
    Request body for POST /refunds/
    Matches all fields used in service.create_refund():
    - payment_intent_id → identifies which payment to refund
    - amount            → optional for partial refund (in cents)
    - reason            → optional, must be a Stripe-accepted value
    """
    payment_intent_id: str = Field(..., description="Stripe PaymentIntent ID to refund (pi_xxx)")
    amount: Optional[int] = Field(
        default=None,
        gt=0,
        description="Partial refund amount in cents (e.g. 500 = $5.00). Omit for full refund."
    )
    reason: Optional[RefundReason] = Field(
        default=None,
        description="Refund reason: duplicate | fraudulent | requested_by_customer"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "payment_intent_id": "pi_3OxxxxxxxxxxxxxxxxxxxxXx",
                "reason": "requested_by_customer"
            }
        }


class RefundResponse(BaseModel):
    """
    Response body for POST /refunds/
    Matches exactly how router.py constructs it:
    RefundResponse(refund_id=r.id, amount=r.amount, currency=r.currency, status=r.status)
    """
    refund_id: str = Field(..., description="Stripe Refund ID (re_xxx)")
    amount: int = Field(..., description="Refunded amount in cents")
    currency: str = Field(..., description="3-letter ISO currency code")
    status: str = Field(..., description="Refund status: succeeded | pending | failed | canceled")

    class Config:
        json_schema_extra = {
            "example": {
                "refund_id": "re_3OxxxxxxxxxxxxxxxxxxxxXx",
                "amount": 2000,
                "currency": "usd",
                "status": "succeeded"
            }
        }