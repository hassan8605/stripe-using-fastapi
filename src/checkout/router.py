import stripe as stripe_lib
import logging
from fastapi import APIRouter, HTTPException

from src.checkout.schema import CreateCheckoutSessionRequest, CheckoutSessionResponse
from src.checkout import service
from src.utils import stripe_error_message

router = APIRouter(prefix="/checkout", tags=["Checkout Sessions"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=CheckoutSessionResponse, summary="Create Checkout Session")
def create_checkout_session(data: CreateCheckoutSessionRequest):
    """
    ## Create a Stripe Checkout Session

    Returns a hosted URL — redirect your user to it.
    Stripe handles everything: card input, 3DS, Apple Pay, Google Pay.

    **After payment:**
    - User lands on `success_url` with `?session_id=cs_xxx`
    - Call GET /checkout/{session_id} to verify `payment_status == paid`
    - Also listen for webhook `checkout.session.completed` for reliability
    """
    try:
        session = service.create_checkout_session(data)
        return CheckoutSessionResponse(session_id=session.id, url=session.url)
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))


@router.get("/{session_id}", summary="Get Checkout Session Status")
def get_checkout_session(session_id: str):
    """Verify payment status after the user returns from Stripe's hosted page."""
    try:
        s = service.retrieve_checkout_session(session_id)
        return {
            "session_id": s.id,
            "payment_status": s.payment_status,   # paid | unpaid | no_payment_required
            "customer_email": s.customer_email,
            "amount_total": s.amount_total,
            "currency": s.currency,
        }
    except stripe_lib.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="Session not found")
