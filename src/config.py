"""
src/config.py
─────────────
Stripe SDK initialization.
Import `stripe` from here anywhere in the project — api_key is already set.
"""

import stripe
from src.settings import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

__all__ = ["stripe"]
