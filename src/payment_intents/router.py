import stripe as stripe_lib
import logging
from fastapi import APIRouter, HTTPException

from src.payment_intents.schema import CreatePaymentIntentRequest, PaymentIntentResponse
from src.payment_intents import service
from src.utils import stripe_error_message

router = APIRouter(prefix="/payment-intents", tags=["Payment Intents"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=PaymentIntentResponse, summary="Create Payment Intent")
def create_payment_intent(data: CreatePaymentIntentRequest):
    """
    ## Create a PaymentIntent (One-Time Payment)

    **Flow:**
    1. Backend creates PaymentIntent → returns `client_secret`
    2. Frontend passes `client_secret` to `stripe.confirmCardPayment()`
    3. Stripe processes → redirects / shows result
    4. Webhook fires `payment_intent.succeeded` to your backend

    **Test payment methods (use in confirm endpoint):**
    - `pm_card_visa` → success
    - `pm_card_visa_debit` → success (debit)
    - `pm_card_threeDSecure2Required` → triggers 3DS
    - `pm_card_chargeDeclined` → decline
    """
    try:
        pi = service.create_payment_intent(data)
        return PaymentIntentResponse(
            id=pi.id,
            client_secret=pi.client_secret,
            amount=pi.amount,
            currency=pi.currency,
            status=pi.status,
            description=pi.description,
        )
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))


@router.get("/{pi_id}", summary="Get Payment Intent")
def get_payment_intent(pi_id: str):
    try:
        pi = service.retrieve_payment_intent(pi_id)
        return {"id": pi.id, "amount": pi.amount, "currency": pi.currency, "status": pi.status}
    except stripe_lib.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="PaymentIntent not found")


@router.post("/{pi_id}/confirm", summary="Confirm Payment Intent (Test/Server Use)")
def confirm_payment_intent(pi_id: str, payment_method: str = "pm_card_visa"):
    """
    Confirm a PaymentIntent server-side.
    Use this for testing only — in production the frontend confirms via Stripe.js.
    """
    try:
        pi = service.confirm_payment_intent(pi_id, payment_method)
        return {"id": pi.id, "status": pi.status}
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))


@router.post("/{pi_id}/cancel", summary="Cancel Payment Intent")
def cancel_payment_intent(pi_id: str):
    try:
        pi = service.cancel_payment_intent(pi_id)
        return {"id": pi.id, "status": pi.status}
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))


@router.get("/", summary="List Payment Intents")
def list_payment_intents(limit: int = 10):
    pis = service.list_payment_intents(limit)
    return [{"id": pi.id, "amount": pi.amount, "currency": pi.currency, "status": pi.status} for pi in pis]
