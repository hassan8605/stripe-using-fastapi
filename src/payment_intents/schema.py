from pydantic import BaseModel, Field
from typing import Optional


class CreatePaymentIntentRequest(BaseModel):
    """
    Request body for POST /payment-intents/
    Matches all fields accessed in service.create_payment_intent()
    """
    amount: int = Field(..., gt=0, description="Amount in cents. e.g. 2000 = $20.00")
    currency: str = Field(default="usd", description="3-letter ISO currency code")
    description: Optional[str] = Field(default=None, description="Internal note shown in Stripe Dashboard")
    customer_id: Optional[str] = Field(default=None, description="Attach to an existing Stripe Customer (cus_xxx)")
    metadata: Optional[dict] = Field(default=None, description="Key-value pairs for your internal records")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 2000,
                "currency": "usd",
                "description": "Order #1234",
                "customer_id": "cus_xxxxxxxxxxxxxxxx",
                "metadata": {"order_id": "1234", "user_id": "42"}
            }
        }


class PaymentIntentResponse(BaseModel):
    """
    Response body for POST /payment-intents/
    Matches all fields used in router.py:
    PaymentIntentResponse(id, client_secret, amount, currency, status, description)
    """
    id: str = Field(..., description="Stripe PaymentIntent ID (pi_xxx)")
    client_secret: str = Field(..., description="Pass this to Stripe.js on the frontend to confirm payment")
    amount: int = Field(..., description="Amount in cents")
    currency: str = Field(..., description="3-letter ISO currency code")
    status: str = Field(..., description="PaymentIntent lifecycle status")
    description: Optional[str] = Field(default=None, description="Description set at creation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "pi_3OxxxxxxxxxxxxxxxxxxxxXx",
                "client_secret": "pi_3OxxxxxxxxxxxxxxxxxxxxXx_secret_xxxxxxxx",
                "amount": 2000,
                "currency": "usd",
                "status": "requires_payment_method",
                "description": "Order #1234"
            }
        }