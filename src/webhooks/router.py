"""
webhooks/router.py
──────────────────
Stripe sends events to this endpoint for EVERYTHING that happens:
payment success, subscription renewal, invoice failure, etc.

⚠️  CRITICAL RULES:
  1. Always verify the signature (we do this in service.py)
  2. Return 200 quickly — do heavy work async (queues, background tasks)
  3. Make handlers IDEMPOTENT — Stripe retries failed webhooks
  4. Never trust webhook data without verifying signature first

Setup:
  Local dev:  stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
  Production: Dashboard → Developers → Webhooks → Add Endpoint
"""

import stripe as stripe_lib
import logging
from fastapi import APIRouter, HTTPException, Request, Header

from src.webhooks.service import verify_and_construct_event

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


@router.post("/stripe", summary="Stripe Webhook Handler")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="stripe-signature"),
):
    """
    ## Stripe Webhook Receiver

    **Local Dev Setup:**
    ```bash
    # 1. Install Stripe CLI
    brew install stripe/stripe-cli/stripe

    # 2. Login
    stripe login

    # 3. Forward events to your local server
    stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe

    # 4. Copy the printed webhook secret → paste in .env as STRIPE_WEBHOOK_SECRET
    ```

    **Production Setup (Dashboard):**
    1. Developers → Webhooks → Add Endpoint
    2. URL: `https://yourdomain.com/api/v1/webhooks/stripe`
    3. Select events (see list below)
    4. Copy signing secret → set as `STRIPE_WEBHOOK_SECRET`

    **Events to subscribe to:**
    - `payment_intent.succeeded`
    - `payment_intent.payment_failed`
    - `checkout.session.completed`
    - `customer.subscription.created/updated/deleted`
    - `invoice.paid`
    - `invoice.payment_failed`
    """
    payload = await request.body()

    # ── Step 1: Verify signature ──────────────────────────────────────────────
    try:
        event = verify_and_construct_event(payload, stripe_signature)
    except stripe_lib.error.SignatureVerificationError:
        logger.error("❌ Invalid Stripe webhook signature — possible spoofed request")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    except Exception as e:
        logger.error(f"❌ Webhook construction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    event_type: str = event["type"]
    data: dict = event["data"]["object"]

    logger.info(f"📨 Stripe event received: {event_type} | id={event['id']}")

    # ── Step 2: Handle events ─────────────────────────────────────────────────

    # ── Payment Intent ────────────────────────────────────────────────────────
    if event_type == "payment_intent.succeeded":
        pi_id = data["id"]
        amount = data["amount"]
        currency = data["currency"]
        customer = data.get("customer")
        logger.info(f"✅ Payment succeeded | pi={pi_id} | amount={amount} {currency} | customer={customer}")
        # TODO: Mark order as paid in DB, send confirmation email, fulfill order

    elif event_type == "payment_intent.payment_failed":
        pi_id = data["id"]
        error = data.get("last_payment_error", {})
        reason = error.get("message", "Unknown") if error else "Unknown"
        logger.warning(f"❌ Payment failed | pi={pi_id} | reason={reason}")
        # TODO: Notify customer, update order status, trigger retry logic

    elif event_type == "payment_intent.canceled":
        logger.info(f"🚫 Payment canceled | pi={data['id']}")
        # TODO: Release reserved inventory

    # ── Checkout Session ──────────────────────────────────────────────────────
    elif event_type == "checkout.session.completed":
        session_id = data["id"]
        payment_status = data.get("payment_status")
        customer_email = data.get("customer_email")
        logger.info(f"🛒 Checkout completed | session={session_id} | status={payment_status} | email={customer_email}")
        # TODO: Fulfill the order, provision access, send receipt

    elif event_type == "checkout.session.expired":
        logger.info(f"⏰ Checkout session expired | session={data['id']}")
        # TODO: Release held inventory

    # ── Subscriptions ─────────────────────────────────────────────────────────
    elif event_type == "customer.subscription.created":
        logger.info(f"📅 Subscription created | sub={data['id']} | status={data['status']}")
        # TODO: Provision product access for the customer

    elif event_type == "customer.subscription.updated":
        logger.info(f"🔄 Subscription updated | sub={data['id']} | status={data['status']}")
        # TODO: Update user plan in DB (upgrades, downgrades, pauses)

    elif event_type == "customer.subscription.deleted":
        logger.info(f"🗑️ Subscription canceled | sub={data['id']} | customer={data['customer']}")
        # TODO: Revoke product access

    # ── Invoices ──────────────────────────────────────────────────────────────
    elif event_type == "invoice.paid":
        invoice_id = data["id"]
        customer_id = data["customer"]
        amount_paid = data["amount_paid"]
        logger.info(f"🧾 Invoice paid | invoice={invoice_id} | customer={customer_id} | amount={amount_paid}")
        # TODO: Extend subscription access period, send receipt email

    elif event_type == "invoice.payment_failed":
        customer_id = data["customer"]
        attempt = data.get("attempt_count", 1)
        logger.warning(f"⚠️ Invoice payment failed | customer={customer_id} | attempt #{attempt}")
        # TODO: Notify customer to update payment method, possibly suspend access

    elif event_type == "invoice.upcoming":
        logger.info(f"📬 Upcoming invoice | customer={data['customer']}")
        # TODO: Send renewal reminder email

    else:
        logger.debug(f"ℹ️ Unhandled event type: {event_type}")

    # ── Step 3: Always return 200 ─────────────────────────────────────────────
    # Non-2xx response = Stripe retries the webhook (up to 3 days)
    return {"received": True, "event_type": event_type}
