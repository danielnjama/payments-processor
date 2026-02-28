# Payment Service (Daraja M-Pesa Integration)

## Overview

This Django-based **Payment Service** acts as a centralized payment
gateway for multiple applications. It integrates with Safaricom's
**Daraja API** to process and record both **STK Push** and **C2B**
M-Pesa payments.

This service is designed as a **multi-tenant reusable microservice**.

External applications can:

-   Initiate STK Push requests
-   Receive payment confirmations
-   Verify payment status
-   Prevent duplicate payment usage
-   Claim payments securely
-   Consume shared C2B intake payments

------------------------------------------------------------------------

## Updated Architecture

    External App → Payment Service → Safaricom Daraja API
                         ↓
                   Payment Database
                         ↓
             Claim & Ownership Transfer Logic

### 🔹 STK Flow

App initiates payment → Payment owned by that app → Callback updates →
App claims.

### 🔹 C2B Flow (Shared Intake Model)

Customer pays → Payment stored under **ADMIN_SHOP** →\
Any authorized app can claim → Ownership transfers to claiming app.

------------------------------------------------------------------------

## Admin Shop Concept (C2B Intake Owner)

To support generic C2B payments (Paybill / Till):

-   A default system app called **ADMIN_SHOP** is created.
-   All C2B confirmations are saved under this app.
-   When an external app claims the payment:
    -   Ownership is transferred to that app
    -   Payment is marked as claimed

This ensures: - Multi-tenant safety - No cross-app payment theft - Clean
accounting trail

------------------------------------------------------------------------

## Features Implemented

### ✔ STK Push Initiation

### ✔ STK Callback Handling

### ✔ C2B Confirmation Endpoint

### ✔ Shared Admin Intake Model

### ✔ Ownership Transfer on Claim

### ✔ API Key Authentication

### ✔ Payment Verification

### ✔ Claim Protection (No Double Claim)

### ✔ Logging

------------------------------------------------------------------------

## API Endpoints

### 1️⃣ Initiate STK Push

POST `/api/stk-push/`

Headers:

    X-API-KEY: your_api_key
    Content-Type: application/json

Body:

``` json
{
  "phone_number": "254708374149",
  "amount": 10,
  "reference": "ORDER001",
  "description": "Subscription Payment"
}
```

------------------------------------------------------------------------

### 2️⃣ STK Callback (Safaricom)

POST `/api/mpesa/stk-callback/`

Automatically called by Safaricom.

------------------------------------------------------------------------

### 3️⃣ C2B Confirmation

POST `/api/mpesa/c2b-confirmation/`

-   Saves payment under ADMIN_SHOP
-   Marks as SUCCESS
-   Stores raw Safaricom payload

------------------------------------------------------------------------

### 4️⃣ Verify Payment

GET `/api/payments/verify/?receipt=XXXX`

Supports: - Receipt lookup (recommended) - External reference (STK
fallback)

------------------------------------------------------------------------

### 5️⃣ Claim Payment

POST `/api/payments/claim/`

Body:

``` json
{
  "receipt": "XXXX"
}
```

Logic: - Searches SUCCESS payments - Allows lookup from: - Requesting
app - ADMIN_SHOP - If owned by ADMIN_SHOP → transfers ownership - Marks
payment as claimed

------------------------------------------------------------------------

## Updated Payment Model Fields

  Field                  Description
  ---------------------- -------------------------------
  id                     UUID primary key
  app                    Owning ExternalApp
  external_reference     Reference from external app
  phone_number           Customer phone
  amount                 Payment amount
  mpesa_receipt_number   M-Pesa receipt
  checkout_request_id    Daraja checkout ID
  payment_type           STK or C2B
  status                 PENDING / SUCCESS / FAILED
  claimed                Whether payment has been used
  claimed_at             Claim timestamp
  raw_callback           Raw Safaricom response
  created_at             Timestamp

------------------------------------------------------------------------

## Security Design

✔ API Key authentication per app\
✔ Apps cannot access other apps' payments\
✔ Shared C2B intake controlled by ADMIN_SHOP\
✔ Ownership transfer only during claim\
✔ Duplicate claim prevention\
✔ Centralized logging

------------------------------------------------------------------------

## Installation Notes

After deployment, ensure ADMIN_SHOP exists:

``` python
ExternalApp.objects.get_or_create(
    name="ADMIN_SHOP",
    defaults={"is_active": True}
)
```

This can also be implemented in a data migration or post_migrate signal.

------------------------------------------------------------------------

## Testing Flow (Full System)

### STK Test

1.  Create ExternalApp
2.  Send STK request
3.  Confirm PENDING status
4.  Receive callback
5.  Verify SUCCESS
6.  Claim payment

### C2B Test

1.  Simulate C2B confirmation
2.  Confirm payment saved under ADMIN_SHOP
3.  Claim from external app
4.  Confirm ownership transfer

------------------------------------------------------------------------

## Current System Status

### ✅ Fully Implemented

✔ STK Push\
✔ STK Callback\
✔ C2B Confirmation\
✔ Admin Intake Model\
✔ Payment Verification\
✔ Secure Claim Endpoint\
✔ Ownership Transfer\
✔ Logging & Monitoring

------------------------------------------------------------------------

## Design Philosophy

This service is:

-   Decoupled
-   Multi-tenant
-   Secure by default
-   Microservice-ready
-   Production-oriented
-   Built for scale

------------------------------------------------------------------------

## Author

Daniel Njama Wangari\
Dynamic Technologies
