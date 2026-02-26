import stripe as stripe_lib
import logging
from fastapi import APIRouter, HTTPException

from src.customers.schema import CreateCustomerRequest, CustomerResponse, PaymentMethodResponse
from src.customers import service
from src.utils import stripe_error_message

router = APIRouter(prefix="/customers", tags=["Customers"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=CustomerResponse, summary="Create Customer")
def create_customer(data: CreateCustomerRequest):
    """
    Create a Stripe Customer object.

    **Why create customers?**
    - Attach subscriptions to them
    - Save cards for future charges (no re-entering card details)
    - View full charge history in Stripe Dashboard
    """
    try:
        c = service.create_customer(data)
        return CustomerResponse(customer_id=c.id, email=c.email, name=c.name, created=c.created)
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))


@router.get("/{customer_id}", summary="Get Customer")
def get_customer(customer_id: str):
    try:
        c = service.get_customer(customer_id)
        return {"customer_id": c.id, "email": c.email, "name": c.name, "created": c.created}
    except stripe_lib.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="Customer not found")


@router.get("/", summary="List Customers")
def list_customers(limit: int = 10):
    customers = service.list_customers(limit)
    return [{"customer_id": c.id, "email": c.email, "name": c.name} for c in customers]


@router.delete("/{customer_id}", summary="Delete Customer")
def delete_customer(customer_id: str):
    try:
        result = service.delete_customer(customer_id)
        return {"deleted": result.deleted, "customer_id": result.id}
    except stripe_lib.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="Customer not found")


@router.get("/{customer_id}/payment-methods", response_model=list[PaymentMethodResponse], summary="List Saved Cards")
def list_payment_methods(customer_id: str, type: str = "card"):
    """List all saved payment methods (cards) attached to a customer."""
    pms = service.list_payment_methods(customer_id, type)
    result = []
    for pm in pms:
        card_data = None
        if pm.card:
            card_data = {
                "brand": pm.card.brand,
                "last4": pm.card.last4,
                "exp_month": pm.card.exp_month,
                "exp_year": pm.card.exp_year,
            }
        result.append({"id": pm.id, "type": pm.type, "card": card_data})
    return result


@router.delete("/payment-methods/{payment_method_id}", summary="Detach Payment Method")
def detach_payment_method(payment_method_id: str):
    """Remove a saved card from its customer."""
    try:
        pm = service.detach_payment_method(payment_method_id)
        return {"id": pm.id, "message": "Payment method detached successfully"}
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))
