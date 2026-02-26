"""
main.py — Entry point for Stripe Payment API
Matches project structure of ALMANA-CMS-BE
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.settings import settings
from src.logging_config import setup_logging
from src.middlewares import RequestLoggingMiddleware

# ── Feature Routers ────────────────────────────────────────────────────────────
from src.customers.router import router as customers_router
from src.payment_intents.router import router as payment_intents_router
from src.checkout.router import router as checkout_router
from src.subscriptions.router import router as subscriptions_router
from src.refunds.router import router as refunds_router
from src.webhooks.router import router as webhooks_router


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


# ── App Instance ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## 💳 Stripe Payment API

Production-ready FastAPI backend covering all major Stripe payment features.

### Modules
- **Customers** — create, retrieve, list, delete + saved payment methods
- **Payment Intents** — one-time payment full lifecycle
- **Checkout Sessions** — Stripe-hosted payment page
- **Subscriptions** — recurring billing lifecycle
- **Refunds** — full & partial refunds
- **Webhooks** — verified event handler

### Test Cards
| Card | Result |
|------|--------|
| `4242 4242 4242 4242` | ✅ Success |
| `4000 0025 0000 3155` | 🔐 3D Secure |
| `4000 0000 0000 9995` | ❌ Declined |
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middlewares ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# ── Routers ────────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(customers_router,       prefix=PREFIX)
app.include_router(payment_intents_router, prefix=PREFIX)
app.include_router(checkout_router,        prefix=PREFIX)
app.include_router(subscriptions_router,   prefix=PREFIX)
app.include_router(refunds_router,         prefix=PREFIX)
app.include_router(webhooks_router,        prefix=PREFIX)


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"app": settings.APP_NAME, "status": "running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)