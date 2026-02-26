# 💳 Stripe Payment API — FastAPI

Production-ready Stripe payment backend matching the ALMANA-CMS-BE project structure.

---

## 📁 Project Structure

```
stripe-payment-api/
├── main.py                      # App entry, middleware, router registration
├── pyproject.toml
├── requirements.txt
├── env.example                  # Copy to .env and fill keys
├── .gitignore
│
├── tests/
│   └── test_payments.py
│
└── src/
    ├── __init__.py
    ├── settings.py              # Pydantic settings (reads .env)
    ├── config.py                # Stripe SDK init (import stripe from here)
    ├── schema.py                # Shared base schemas
    ├── models.py                # Shared enums: Currency, Status, etc.
    ├── response.py              # Standardized JSON response helpers
    ├── utils.py                 # cents↔dollars, timestamps, error messages
    ├── logging_config.py        # Centralized logging setup
    ├── middlewares.py           # Request logging middleware
    │
    ├── customers/               # 👤 Customer CRUD + saved payment methods
    │   ├── __init__.py
    │   ├── schema.py
    │   ├── service.py           # All Stripe Customer API calls
    │   └── router.py            # FastAPI endpoints
    │
    ├── payment_intents/         # 💳 One-time payment lifecycle
    │   ├── __init__.py
    │   ├── schema.py
    │   ├── service.py
    │   └── router.py
    │
    ├── checkout/                # 🛒 Stripe-hosted payment page
    │   ├── __init__.py
    │   ├── schema.py
    │   ├── service.py
    │   └── router.py
    │
    ├── subscriptions/           # 🔄 Recurring billing
    │   ├── __init__.py
    │   ├── schema.py
    │   ├── service.py
    │   └── router.py
    │
    ├── refunds/                 # 💰 Full & partial refunds
    │   ├── __init__.py
    │   ├── schema.py
    │   ├── service.py
    │   └── router.py
    │
    └── webhooks/                # 📡 Stripe event listener
        ├── __init__.py
        ├── service.py           # Signature verification
        └── router.py            # Event handlers
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp env.example .env
# Edit .env and fill in your Stripe keys
```

### 3. Get Stripe Keys (Dashboard)
1. Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. Make sure you're in **Test Mode** (toggle top-left)
3. **Developers → API Keys** → copy `Secret key` and `Publishable key`

### 4. Set up local webhooks
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe    # macOS
# Windows: https://github.com/stripe/stripe-cli/releases

stripe login
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
# Copy the printed whsec_xxx → paste in .env as STRIPE_WEBHOOK_SECRET
```

### 5. Run the server
```bash
uvicorn main:app --reload
```

Open **http://localhost:8000/docs** to explore all endpoints.

---

## 📡 API Endpoints

| Module | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| Customers | POST | `/api/v1/customers/` | Create customer |
| Customers | GET | `/api/v1/customers/{id}` | Get customer |
| Customers | GET | `/api/v1/customers/` | List customers |
| Customers | DELETE | `/api/v1/customers/{id}` | Delete customer |
| Customers | GET | `/api/v1/customers/{id}/payment-methods` | List saved cards |
| Customers | DELETE | `/api/v1/customers/payment-methods/{pm_id}` | Remove saved card |
| Payment Intents | POST | `/api/v1/payment-intents/` | Create payment intent |
| Payment Intents | GET | `/api/v1/payment-intents/{id}` | Get payment intent |
| Payment Intents | POST | `/api/v1/payment-intents/{id}/confirm` | Confirm (test) |
| Payment Intents | POST | `/api/v1/payment-intents/{id}/cancel` | Cancel |
| Payment Intents | GET | `/api/v1/payment-intents/` | List recent |
| Checkout | POST | `/api/v1/checkout/` | Create hosted checkout |
| Checkout | GET | `/api/v1/checkout/{id}` | Get session status |
| Subscriptions | POST | `/api/v1/subscriptions/` | Create subscription |
| Subscriptions | GET | `/api/v1/subscriptions/{id}` | Get subscription |
| Subscriptions | DELETE | `/api/v1/subscriptions/{id}` | Cancel subscription |
| Subscriptions | GET | `/api/v1/subscriptions/customer/{id}` | List by customer |
| Refunds | POST | `/api/v1/refunds/` | Create refund |
| Webhooks | POST | `/api/v1/webhooks/stripe` | Receive Stripe events |

---

## 🧪 Test Cards

| Card Number | Result |
|-------------|--------|
| `4242 4242 4242 4242` | ✅ Success |
| `4000 0025 0000 3155` | 🔐 Requires 3D Secure |
| `4000 0000 0000 9995` | ❌ Card declined |
| `4100 0000 0000 0019` | 🚨 Fraud detection |

Use any future expiry (e.g. `12/34`), any 3-digit CVC, any ZIP.

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 🎓 Interview Cheat Sheet

### Core Objects

| Object | Purpose |
|--------|---------|
| **Customer** | Stores email, name, saved payment methods. Required for subscriptions. |
| **PaymentIntent** | Central object for one-time payments. Has a full lifecycle. Returns `client_secret`. |
| **Checkout Session** | Stripe-hosted payment page. Redirect user to `session.url`. |
| **Subscription** | Recurring billing. Auto-charges on schedule. Managed via invoices. |
| **PaymentMethod** | Represents a card/bank/wallet. Attach to Customer for reuse. |
| **Refund** | Reverses a charge. Full or partial. Takes 5–10 business days. |
| **Webhook** | HTTP POST from Stripe when events happen. ALWAYS verify signature. |

### PaymentIntent Lifecycle
```
requires_payment_method
    → requires_confirmation
    → requires_action       ← 3DS / SCA happens here
    → processing
    → succeeded ✅  |  canceled ❌
```

### Key Interview Questions

**Q: PaymentIntent vs Charge?**
`Charge` is the legacy API. `PaymentIntent` is modern, handles SCA/3DS (required in EU), and tracks the full payment lifecycle.

**Q: Why verify webhook signatures?**
Anyone can POST to your webhook URL. Stripe signs each request with `STRIPE_WEBHOOK_SECRET` using HMAC-SHA256. Without verification, attackers can spoof fake payment success events.

**Q: How do subscription renewals work?**
You don't charge manually. Stripe auto-creates invoices on renewal and fires `invoice.paid` or `invoice.payment_failed`. Your backend listens and updates DB accordingly.

**Q: What is idempotency in Stripe?**
Pass `idempotency_key` to prevent double-charging on network timeouts/retries. Stripe deduplicates requests with the same key within 24 hours.

**Q: What is SCA / 3D Secure?**
Strong Customer Authentication — required by European banks (PSD2). Stripe handles it via PaymentIntents. If required, status becomes `requires_action` and Stripe.js shows the popup.

**Q: What happens if webhook returns non-200?**
Stripe retries with exponential backoff over 3 days. This is why handlers must be **idempotent** — the same event may arrive multiple times.

---

## 🔧 Production Checklist

- [ ] Switch to live Stripe keys (`sk_live_`, `pk_live_`)
- [ ] Set `DEBUG=False`, `ENVIRONMENT=production`
- [ ] Store secrets in env vars (never hardcode)
- [ ] Use HTTPS everywhere
- [ ] Add database to persist orders/subscriptions
- [ ] Implement idempotency keys on payment creation
- [ ] Make webhook handlers idempotent (safe to run twice)
- [ ] Set up Stripe Radar (fraud detection)
- [ ] Configure webhook retry alerting
