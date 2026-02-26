from pydantic import BaseModel, Field
from typing import Optional


class LineItem(BaseModel):
    """
    Single product/service in the checkout.
    amount is in cents (e.g. 4999 = $49.99)
    """
    name: str
    amount: int = Field(..., gt=0, description="Price in cents. e.g. 4999 = $49.99")
    quantity: int = Field(default=1, gt=0)
    currency: str = Field(default="usd", description="3-letter ISO currency code")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Pro Plan",
                "amount": 4999,
                "quantity": 1,
                "currency": "usd"
            }
        }


class CreateCheckoutSessionRequest(BaseModel):
    """
    Request body for POST /checkout/
    Matches what service.create_checkout_session() expects.
    """
    line_items: list[LineItem] = Field(..., min_length=1, description="At least one item required")
    customer_email: Optional[str] = Field(default=None, description="Pre-fill customer email on Stripe's page")
    success_url: Optional[str] = Field(default=None, description="Redirect URL after successful payment. Defaults to FRONTEND_URL/success")
    cancel_url: Optional[str] = Field(default=None, description="Redirect URL if user cancels. Defaults to FRONTEND_URL/cancel")
    metadata: Optional[dict] = Field(default=None, description="Key-value pairs for your internal records")

    class Config:
        json_schema_extra = {
            "example": {
                "line_items": [
                    {"name": "Pro Plan", "amount": 4999, "quantity": 1},
                    {"name": "Setup Fee", "amount": 999, "quantity": 1}
                ],
                "customer_email": "user@example.com",
                "metadata": {"user_id": "42", "plan": "pro"}
            }
        }


class CheckoutSessionResponse(BaseModel):
    """
    Response body for POST /checkout/
    Matches what router.py returns from service.create_checkout_session().
    """
    session_id: str = Field(..., description="Stripe Checkout Session ID (cs_xxx)")
    url: str = Field(..., description="Redirect the user to this URL to complete payment")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "cs_test_a1b2c3d4e5f6",
                "url": "https://checkout.stripe.com/pay/cs_test_a1b2c3d4e5f6"
            }
        }