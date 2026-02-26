import stripe as stripe_lib
import logging
from fastapi import APIRouter, HTTPException

from src.subscriptions.schema import CreateSubscriptionRequest, SubscriptionResponse
from src.subscriptions import service
from src.utils import stripe_error_message, format_stripe_timestamp

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
logger = logging.getLogger(__name__)


@router.post("/", summary="Create Subscription")
def create_subscription(data: CreateSubscriptionRequest):
    """
    ## Create a Recurring Subscription

    **Pre-requisite (Dashboard):**
    1. Dashboard → Products → Add Product
    2. Add Pricing → Recurring → set amount
    3. Copy **Price ID** (`price_xxx`) and use as `price_id`

    **After creating:**
    - Status is `incomplete` until first payment
    - Use returned `client_secret` on frontend: `stripe.confirmCardPayment(client_secret)`
    - Once paid → status becomes `active`
    - Stripe auto-renews and fires webhooks on each invoice
    """
    try:
        sub = service.create_subscription(data)
        client_secret = None
        try:
            client_secret = sub.latest_invoice.payment_intent.client_secret
        except AttributeError:
            pass

        return {
            "subscription_id": sub.id,
            "customer_id": sub.customer,
            "status": sub.status,
            "current_period_end": sub.current_period_end,
            "client_secret": client_secret,
        }
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))


@router.get("/{sub_id}", summary="Get Subscription")
def get_subscription(sub_id: str):
    try:
        sub = service.retrieve_subscription(sub_id)
        return {
            "subscription_id": sub.id,
            "status": sub.status,
            "current_period_end": format_stripe_timestamp(sub.current_period_end),
            "cancel_at_period_end": sub.cancel_at_period_end,
        }
    except stripe_lib.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="Subscription not found")


@router.delete("/{sub_id}", summary="Cancel Subscription")
def cancel_subscription(sub_id: str, immediately: bool = True):
    """
    - `immediately=true` → cancel now
    - `immediately=false` → cancel at billing period end (user keeps access)
    """
    try:
        sub = service.cancel_subscription(sub_id, immediately)
        return {
            "subscription_id": sub.id,
            "status": sub.status,
            "cancel_at_period_end": sub.cancel_at_period_end,
        }
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))


@router.get("/customer/{customer_id}", summary="List Customer Subscriptions")
def list_subscriptions(customer_id: str):
    subs = service.list_subscriptions(customer_id)
    return [
        {
            "subscription_id": s.id,
            "status": s.status,
            "current_period_end": format_stripe_timestamp(s.current_period_end),
        }
        for s in subs
    ]
