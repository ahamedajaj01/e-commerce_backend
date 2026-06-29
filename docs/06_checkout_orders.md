# 🛒 Checkout & Orders Documentation

This document explains how the purchase journey works in the backend and how the frontend should interact with the Checkout Orchestration layer.

---

## 1. The Core Philosophy
We separate **Checkout** from **Orders** to prevent database pollution.
*   **CheckoutSession:** A temporary "Draft" state. It stores the customer's form data, calculates prices, and "freezes" the data so it doesn't change during payment.
*   **Order:** A permanent record created **only** after the checkout is successfully completed. At this point, inventory is **automatically deducted**.

---

## 2. The Buyer's Journey (Flow)

### Step 1: Initialize Checkout
User fills in name, address, and shipping choice. **Payment method is NOT required here.**

*   **Action:** `POST /api/v1/checkout/storefront/sessions/`
*   **Body:**
    ```json
    {
      "name": "Ajaj Ahamed",
      "email": "user@example.com",
      "phone": "9821XXXXXX",
      "province": "Bagmati",
      "district": "Kathmandu",
      "city": "Kathmandu",
      "street": "Maitighar",
      "shipping_rule_id": "uuid-here"
    }
    ```
*   **Result:** Returns a `CheckoutSession` with pricing locked in. No `payment_method` in response yet.

### Step 2: Select Payment Method
User views the order summary and selects how to pay.

*   **Action:** `PATCH /api/v1/checkout/storefront/sessions/{uuid}/`
*   **Body:**
    ```json
    { "payment_method": "ESEWA" }
    ```
*   Available values: `COD`, `BANK`, `ESEWA`, `KHALTI`, `ONLINE`

### Step 3: Complete & Convert
User clicks "Confirm Order". Backend validates stock one final time, creates the permanent Order, and deducts inventory atomically.

*   **Action:** `POST /api/v1/checkout/storefront/sessions/{uuid}/complete/`
*   **Returns:** `{"order_number": "ORD-2026...", "order_id": "uuid"}`
*   **Error:** Returns `400` with message like `"Insufficient stock for Kurti (KRT-WHT-M). Available: 0"` if stock ran out during the session.

---

## 3. Key Concepts

### 🚚 Dynamic Delivery Estimation (The Total ETA)
The system automatically calculates the arrival date by summing two different parts:
1.  **Warehouse Dispatch:** How long it takes to pack the item (from Product settings).
2.  **Courier Transit:** How long it takes to reach the destination city (from Shipping Rule).
3.  **Total:** Customer sees something like **"5-8 business days"**.

### 📸 Data Snapshotting
Once a `CheckoutSession` is created, the price and shipping fee are **locked**. Price changes in the catalog don't affect in-flight checkouts.

### 📦 Inventory Deduction
When `complete/` is called, the backend:
1. Re-validates every item's `stock_quantity` in real-time.
2. Deducts stock atomically for each `OrderItem` created.
3. Logs a `StockMovement` record (type: `OUT`) for each item for audit purposes.

---

## 4. Order Lifecycle Statuses

### Order Status (`status`)

| Code | Display | Progress |
|------|---------|----------|
| `PENDING` | Pending | 20% |
| `CONFIRMED` | Confirmed | 40% |
| `PROCESSING` | Processing | 60% |
| `SHIPPED` | Shipped | 80% |
| `DELIVERED` | Delivered | 100% |
| `CANCELLED` | Cancelled | 0% |

### Payment Status (`payment_status`)

| Code | Display | Description |
|------|---------|-------------|
| `UNPAID` | Unpaid | Default for new orders |
| `AWAITING_VERIFICATION` | Awaiting Verification | Customer uploaded payment proof |
| `PAID` | Payment Verified | Admin confirmed receipt of funds |
| `FAILED` | Failed / Rejected | Payment proof was invalid |
| `REFUNDED` | Refunded | Funds returned to customer |

> These two statuses are independent. An order can be `CONFIRMED` (fulfillment) while still `AWAITING_VERIFICATION` (finance). This is by design.

---

## 5. Admin Update Endpoint

`PATCH /api/v1/backoffice/orders/{id}/`

```json
{
  "status": "CONFIRMED",
  "payment_status": "PAID",
  "notes": "Verified eSewa screenshot and confirmed for shipping."
}
```

---

## 6. Order Detail Response

`GET /api/v1/backoffice/orders/{id}/`

Includes:
- Full customer and shipping snapshot
- `items[]` — each with `variant_image` (the exact image the customer selected) and `image` (live fallback)
- `transactions[]` — payment attempts with nested `proofs[]` (uploaded screenshots)
- `status_history[]` — full audit trail of every status change

---

## 7. Future Proofing: Payment Gateways

To add a new provider (eSewa, Khalti):
1. Frontend selects `payment_method: "ESEWA"` via PATCH on the session.
2. On gateway success callback, call `complete/` with the `payment_id`.
3. The `OrderService` detects a non-empty `payment_id` and auto-marks the order as `PAID`.
