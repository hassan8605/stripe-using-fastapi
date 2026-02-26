import stripe as stripe_lib
import logging
from fastapi import APIRouter, HTTPException

from src.refunds.schema import CreateRefundRequest, RefundResponse
from src.refunds import service
from src.utils import stripe_error_message

router = APIRouter(prefix="/refunds", tags=["Refunds"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=RefundResponse, summary="Create Refund")
def create_refund(data: CreateRefundRequest):
    """
    ## Refund a Payment

    - **Full refund** → omit `amount`
    - **Partial refund** → set `amount` in cents (e.g. `500` = $5.00)
    - **Reason options:** `duplicate`, `fraudulent`, `requested_by_customer`

    Refunds take 5–10 business days to appear on the customer's card statement.
    Stripe's processing fee is not returned to you.
    """
    try:
        r = service.create_refund(data)
        return RefundResponse(refund_id=r.id, amount=r.amount, currency=r.currency, status=r.status)
    except stripe_lib.error.StripeError as e:
        raise HTTPException(status_code=400, detail=stripe_error_message(e))
