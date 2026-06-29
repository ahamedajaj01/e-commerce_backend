# 📦 Order Management Documentation

The **Order Module** is the immutable source of truth for the business. Once a checkout is completed, all relevant data is snapshotted into this module as a permanent record.

---

## 1. Core Architecture

### 🧱 Models
*   **Order**: The main aggregate. Stores financial totals, customer info, and current status.
*   **OrderItem**: A snapshot of each product variant purchased (Price, SKU, Name).
*   **OrderStatusHistory**: An audit trail of every status transition.

---

## 2. Order Lifecycle

The system follows a strict state-machine flow:

1.  **PENDING**: Order created, awaiting confirmation or processing.
2.  **CONFIRMED**: Payment verified or COD confirmed.
3.  **PROCESSING**: Warehouse is picking and packing.
4.  **SHIPPED**: Handed over to the courier.
5.  **DELIVERED**: Customer received the package.
6.  **CANCELLED**: Terminated.

---

## 3. Public Order Tracking (NEW) 🚀

This feature allows customers (including Guests) to track their order progress without logging in.

### 🛡️ Privacy & Anonymization
To protect customer data, the public tracking API **strips out** all PII (Personally Identifiable Information). 
- **HIDDEN**: Customer name, email, phone, shipping address, internal notes, and item list.
- **SHOWN**: Order reference, status, payment status, ETA, and a simplified status timeline.

### 🔗 Tracking API
`GET /api/v1/storefront/orders/track/?number=ORD-20260624-XXXXXX`

**Success Response:**
```json
{
  "success": true,
  "data": {
    "order_number": "ORD-20260624-9B2A4F",
    "status": "PROCESSING",
    "payment_status": "PAID",
    "arrival_estimate": "2-5 business days",
    "status_timeline": [
      { "new_status": "PENDING", "created_at": "..." },
      { "new_status": "PROCESSING", "created_at": "..." }
    ],
    "created_at": "..."
  }
}
```

---

## 4. API Reference

### 🛍️ Storefront (Buyers)

#### List My Orders (Requires Login)
`GET /api/v1/storefront/orders/`

#### Order Details (Requires Login)
`GET /api/v1/storefront/orders/{uuid}/`

---

### 🛡️ Backoffice (Staff)

#### Search/Filter Orders
`GET /api/v1/backoffice/orders/?status=PENDING&search=Ajaj`

#### Update Status (Audited)
`PATCH /api/v1/backoffice/orders/{uuid}/`
**Body:**
```json
{
  "status": "SHIPPED",
  "notes": "Left the warehouse via Courier Express."
}
```

---

## 5. Technical Implementation Details

### Snapshot Integrity
We do not reference live Catalog prices in Orders. We store the price **at the time of purchase**. If you increase the price of a product tomorrow, older orders will remain unchanged.

### Tracking Logic
The `OrderTrackingView` uses `OrderSelector.get_order_by_number()` to fetch data without requiring a user ID, but it swaps the `OrderDetailSerializer` for the restricted `OrderTrackingSerializer` to ensure zero data leakage.
