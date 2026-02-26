"""
src/logging_config.py
─────────────────────
Centralized logging setup. Called once at app startup in lifespan.
"""

import logging
import sys
from src.settings import settings


def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Silence noisy third-party loggers
    logging.getLogger("stripe").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"✅ Logging configured | level={settings.LOG_LEVEL} | env={settings.ENVIRONMENT}"
    )
