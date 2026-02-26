from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class CreateCustomerRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {"email": "john@example.com", "name": "John Doe"}
        }


class CustomerResponse(BaseModel):
    customer_id: str
    email: str
    name: Optional[str]
    created: int


class PaymentMethodCard(BaseModel):
    brand: str
    last4: str
    exp_month: int
    exp_year: int


class PaymentMethodResponse(BaseModel):
    id: str
    type: str
    card: Optional[PaymentMethodCard] = None
