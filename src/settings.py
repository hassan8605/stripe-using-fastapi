"""
src/settings.py
───────────────
Central configuration loaded from .env
Mirror of your existing settings.py pattern.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "Stripe Payment API"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"          # development | staging | production
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # ── Stripe ────────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
