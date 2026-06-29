# 💳 Payment Module Documentation

The **Payment Module** handles the collection of funds and verification of transactions. It is designed to be "Manual First" but fully scalable for future automated API gateways (eSewa, Khalti, Stripe).

---

## 1. Domain Architecture

### 🧱 Models
*   **PaymentProvider**: The technical "engine" (e.g., "Manual Bank Transfer", "eSewa API").
*   **PaymentMethod**: What the user selects (e.g., "Bank Transfer", "Khalti"). Linked to a provider.
*   **PaymentTransaction**: A specific attempt to pay for an Order.
*   **PaymentProof**: Customer-uploaded images (screenshots/receipts) for manual verification.

### 🔌 Provider vs Method — What is the Difference?
Think of it like this:
*   **Provider** = the engine under the hood. It defines whether the payment is manual or run through an API gateway.
*   **Method** = the customer-facing option. It has the QR code, instructions, and account details.

A single Provider (e.g., "Manual") can power multiple Methods (e.g., eSewa, Khalti, Bank Transfer).
When you upgrade to eSewa's Merchant API in the future, you only change the **Provider**. The Checkout and Order modules never need to change.

---

## 2. Admin Setup Workflow

Before customers can pay, an admin must configure Providers and Methods.

### Step 1: Create a Provider
`POST /api/v1/backoffice/payments/providers/`
```json
{
  "name": "Manual Provider",
  "provider_type": "MANUAL",
  "is_active": true
}
```
**Provider Types:**
*   `MANUAL` — Admin manually reviews and approves.
*   `GATEWAY` — Future use for automated API integrations.

### Step 2: Create a Payment Method
`POST /api/v1/backoffice/payments/methods/`
```json
{
  "provider": "<provider-uuid>",
  "name": "eSewa",
  "code": "esewa",
  "payment_type": "MANUAL",
  "instructions": "1. Open eSewa app\n2. Send payment to 9812345678\n3. Take a screenshot and upload below.",
  "requires_proof": true,
  "is_active": true,
  "display_order": 1
}
```
*   Upload the `qr_image` separately using `multipart/form-data`.

---

## 3. Storefront Payment Workflow (Buyer)

### Step 1: Customer Selection
The frontend displays active methods.
*   **API:** `GET /api/v1/payments/storefront/methods/`
*   **Response:** Includes `instructions`, `account_details`, and a `qr_image`.

### Step 2: Initialize Transaction
Once the user picks a method.
*   **API:** `POST /api/v1/payments/storefront/transactions/`
*   **Payload:** `{"order_id": "...", "payment_method_id": "..."}`

### Step 3: Proof Submission
The customer pays outside the app (e.g., in their banking app), takes a screenshot, and uploads it.
*   **API:** `POST /api/v1/payments/storefront/transactions/{uuid}/proof/`
*   **FormData:** `image: (file)`

### Step 4: Admin Verification
The admin reviews the screenshot in the backoffice.
*   **API:** `POST /api/v1/backoffice/payments/transactions/{uuid}/verify/`
*   **Payload:** `{"approve": true, "notes": "Verified in bank statement."}`
*   **Result:** If approved, the **Order** automatically marks itself as **PAID**.

---

## 4. Full API Reference

### 🛡️ Backoffice Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` / `POST` | `/api/v1/backoffice/payments/providers/` | List or create Providers |
| `GET` / `POST` | `/api/v1/backoffice/payments/methods/` | List or create Payment Methods |
| `GET` / `PATCH` / `DELETE` | `/api/v1/backoffice/payments/methods/{uuid}/` | Manage a specific method |
| `GET` | `/api/v1/backoffice/payments/transactions/` | List & filter all payment attempts |
| `POST` | `/api/v1/backoffice/payments/transactions/{uuid}/verify/` | Approve or Reject a payment |

### 🛍️ Storefront Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/v1/payments/storefront/methods/` | Active payment options |
| `POST` | `/api/v1/payments/storefront/transactions/` | Start a payment attempt |
| `POST` | `/api/v1/payments/storefront/transactions/{uuid}/proof/` | Upload payment screenshot |

---

## 5. Transaction Status Lifecycle

*   `PENDING`: Transaction created but no proof uploaded.
*   `SUBMITTED`: Proof uploaded, awaiting staff review.
*   `APPROVED`: Verified by staff; Order is updated as PAID.
*   `REJECTED`: Invalid proof; Customer must try again.

---

## 6. Domain Integration

The Payment module is **not** the owner of the Order. It only "signals" the Order module when a transaction is verified using the `VerificationService`. This keeps both domains independent and scalable.

---

## 7. Future Scalability

When upgrading to an API Gateway (e.g., eSewa Merchant API):
1. Create a new `PaymentProvider` with `provider_type: GATEWAY`.
2. Store API credentials in the `configuration` JSON field (encrypted in production).
3. Point the eSewa `PaymentMethod` to use this new Gateway provider.
4. No changes required in Checkout or Order modules.
