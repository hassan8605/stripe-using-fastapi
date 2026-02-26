"""
src/utils.py
────────────
Shared utility functions used across modules.
"""

from datetime import datetime
from typing import Optional


def cents_to_dollars(cents: int) -> float:
    """Convert Stripe amount (cents) to human-readable dollars."""
    return round(cents / 100, 2)


def dollars_to_cents(dollars: float) -> int:
    """Convert dollar amount to Stripe cents."""
    return int(dollars * 100)


def format_stripe_timestamp(ts: Optional[int]) -> Optional[str]:
    """Convert Unix timestamp to ISO string."""
    if ts is None:
        return None
    return datetime.utcfromtimestamp(ts).isoformat() + "Z"


def stripe_error_message(e) -> str:
    """Extract a clean user-facing message from a Stripe exception."""
    if hasattr(e, "user_message") and e.user_message:
        return e.user_message
    if hasattr(e, "error") and e.error:
        return getattr(e.error, "message", str(e))
    return str(e)
