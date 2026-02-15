# Payment Service (Daraja M-Pesa Integration)

## Overview

This Django-based **Payment Service** acts as a centralized payment gateway for multiple applications.
It integrates with Safaricom’s **Daraja API** to process and record M-Pesa payments.

External applications can:

* Initiate STK Push requests
* Receive payment confirmations
* Verify payment status
* Prevent duplicate payment usage
* Mark payments as claimed

This service is designed as a **reusable microservice** for handling payments across different systems.

---

## Architecture

```
External App → Payment Service → Safaricom Daraja API
                     ↓
               Payment Database
                     ↓
           External Apps Verify Payments
```

---

## Features Implemented So Far

### ✔ STK Push Initiation

External apps can initiate payment requests.

### ✔ STK Callback Handling

Safaricom callback updates payment status.

### ✔ Centralized Payment Recording

All transactions are stored in a single service.

### ✔ API Key Authentication

Each external application authenticates using a unique API key.

### ✔ Logging

System events are logged to a file for monitoring and debugging.

### ✔ Payment Tracking

Payments store:

* transaction status
* receipt number
* external reference
* claimed/unclaimed state

---

## Project Structure

```
payment_service/
│
├── config/
│
├── payments/
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── authentication.py
│   │   └── urls.py
│   │
│   ├── services/
│   │   └── daraja.py
│   │
│   ├── models.py
│   └── admin.py
│
└── payments.log
```

---

## Installation & Setup

### 1. Clone & Install Dependencies

```bash
pip install django djangorestframework requests python-decouple
```

---

### 2. Create Environment Variables (.env)

```
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/stk-callback/
MPESA_ENVIRONMENT=sandbox
```

---

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 4. Start Server

```bash
python manage.py runserver
```

---

## Authentication (API Key)

Each external app must have an API key.

Create via Django Admin:

**ExternalApp**

* name
* api_key (auto-generated)

Requests must include:

```
X-API-KEY: your_api_key
```

---

## API Endpoints

### 1️⃣ Initiate STK Push

**POST**

```
/api/stk-push/
```

### Headers

```
X-API-KEY: your_api_key
Content-Type: application/json
```

### Body

```json
{
  "phone_number": "254708374149",
  "amount": 10,
  "reference": "ORDER001",
  "description": "Subscription Payment"
}
```

### Response

```json
{
  "message": "STK initiated",
  "payment_id": "uuid",
  "daraja_response": {...}
}
```

---

### 2️⃣ STK Callback Endpoint (Safaricom)

**POST**

```
/api/mpesa/stk-callback/
```

⚠ This endpoint is called by Safaricom automatically.

---

## Payment Model Fields

| Field                | Description                   |
| -------------------- | ----------------------------- |
| id                   | UUID primary key              |
| external_reference   | Reference from external app   |
| app_name             | App initiating payment        |
| phone_number         | Customer phone                |
| amount               | Payment amount                |
| mpesa_receipt_number | M-Pesa receipt                |
| checkout_request_id  | Daraja checkout ID            |
| payment_type         | STK or C2B                    |
| status               | PENDING / SUCCESS / FAILED    |
| claimed              | Whether payment has been used |
| raw_callback         | Raw Safaricom response        |
| created_at           | Timestamp                     |

---

## Logging

Logs are stored in:

```
payments.log
```

Logs include:

* STK initiation attempts
* Callback responses
* Errors and failures

---

## Testing the Service

### Recommended Tools

* Thunder Client (VS Code)
* Postman
* curl
* ngrok (for callback testing)

---

### Test Flow

1. Create ExternalApp and copy API key
2. Send STK request to `/api/stk-push/`
3. Confirm payment saved as **PENDING**
4. Wait for callback or simulate callback
5. Confirm status updates to **SUCCESS**

---

## Sandbox Callback Testing (ngrok)

Safaricom cannot reach localhost.

Use ngrok:

```bash
ngrok http 8000
```

Update callback URL in `.env`:

```
MPESA_CALLBACK_URL=https://your-ngrok-url/api/mpesa/stk-callback/
```

Restart server.

---

## Current Status

### ✅ Ready

✔ STK Push
✔ Callback handling
✔ Logging
✔ API authentication
✔ Payment storage

### 🔜 Next Enhancements

* Payment verification endpoint
* Claim payment endpoint
* Phone number normalization
* Improved error handling
* Callback security validation

---

## Design Philosophy

This service is:

✔ decoupled
✔ reusable
✔ scalable
✔ microservice-ready
✔ production-oriented

---

## Author

**Daniel Njama Wangari**
Dynamic Technologies
