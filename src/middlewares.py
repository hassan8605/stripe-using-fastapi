"""
src/middlewares.py
──────────────────
Custom ASGI middlewares. Mirrors your existing middlewares.py pattern.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every incoming request with method, path, status code, and duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        # Skip health check spam
        if request.url.path not in ("/health", "/"):
            logger.info(
                f"{request.method} {request.url.path} "
                f"→ {response.status_code} [{duration_ms}ms]"
            )
        return response
