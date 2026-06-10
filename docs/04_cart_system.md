# Cart System Documentation

## Overview

The cart system supports both **authenticated users** and **anonymous guests**. It reuses the same `Cart` and `CartItem` models — guest carts are distinguished by a `guest_token` instead of a user FK. On login, guest cart items are automatically merged into the user's cart.

---

## Cart Status Reference

| Status | Description |
|--------|-------------|
| `ACTIVE` | Cart is in use |
| `CHECKED_OUT` | Cart has been converted to an order |
| `EXPIRED` | Guest cart has passed its 30-day TTL |
| `MERGED` | Guest cart was merged into a user cart on login |
| `ABANDONED` | Cart was left inactive (future cleanup job target) |

---

## Guest Cart Flow

1. On first `POST /cart/items`, the backend creates a new Cart with a unique `guest_token`.
2. The token is returned as an **HttpOnly cookie** named `guest_cart_token` (30-day expiry).
3. All subsequent guest cart calls automatically read this cookie — the frontend does nothing extra.
4. On login, the backend detects the cookie, merges the guest cart into the user cart, and **clears the cookie**.

**Cookie Spec:**
```
Name:     guest_cart_token
HttpOnly: true
SameSite: Lax
Max-Age:  2592000  (30 days)
Secure:   true (production only)
```

---

## API Endpoints

All cart endpoints accept both **authenticated** (via `Authorization: Bearer <token>`) and **anonymous** (via `guest_cart_token` cookie) requests.

### 1. Retrieve Cart

Fetches the current active cart with all items, subtotals, and media.

- **Endpoint:** `GET /api/v1/storefront/cart/`
- **Auth:** Optional (JWT or cookie)
- **Response:**
  ```json
  {
      "success": true,
      "data": {
          "id": "uuid",
          "status": "ACTIVE",
          "is_guest": false,
          "items": [
              {
                  "id": "uuid",
                  "variant": { "id": "uuid", "sku": "...", "price": "500.00", "stock_quantity": 20 },
                  "product_name": "Silk Sari",
                  "thumbnail": "/media/products/media/img.jpg",
                  "quantity": 2,
                  "subtotal": "1000.00"
              }
          ],
          "total_quantity": 2,
          "total_price": "1000.00"
      }
  }
  ```
  > If the guest has no existing cart, returns an empty cart object (`items: []`) without creating a new DB record.

### 2. Add to Cart

Adds a specific variant to the cart.

- **Endpoint:** `POST /api/v1/storefront/cart/items`
- **Auth:** Optional
- **Payload:**
  ```json
  { "variant_id": "uuid", "quantity": 1 }
  ```
- **Guest Behavior:** If no `guest_cart_token` cookie exists, one is **set in the response** automatically.

### 3. Update Quantity

- **Endpoint:** `PATCH /api/v1/storefront/cart/items/{item_id}`
- **Payload:** `{ "quantity": 3 }`
- **Note:** Setting quantity to `0` removes the item.

### 4. Remove Item

- **Endpoint:** `DELETE /api/v1/storefront/cart/items/{item_id}`

---

## Login Merge Flow

When a user logs in (`POST /api/v1/auth/login/`):

1. Backend reads `guest_cart_token` from cookies.
2. If found, fetches the guest `Cart` and the user's active `Cart`.
3. Merges all guest items into the user cart:
   - **Existing variants:** Quantities are **summed**, capped at available `stock_quantity`.
   - **New variants:** Transferred directly to user cart.
4. Guest cart is marked `MERGED` and its `guest_token` is cleared.
5. The `guest_cart_token` cookie is deleted from the response.

> Login is **never blocked** if cart merge fails — it degrades gracefully.

---

## Business Rules

1. **Stock Validation:** All stock checks run server-side against `ProductVariant.stock_quantity` at the point of add/update. Never trust client-side totals.
2. **Quantity Cap on Merge:** If merging would exceed available stock, the quantity is capped at the max available stock.
3. **Guest Cart TTL:** Guest carts expire after **30 days**. Expired carts are filtered out of selectors and are not returned as active.
4. **Error Codes:**
   - `INSUFFICIENT_STOCK`: Requested quantity exceeds current stock.
   - `VARIANT_NOT_AVAILABLE`: Variant is deactivated or doesn't exist.

---

## Frontend Integration Guide

1. **On App Load:** Call `GET /cart/` — if the user is authenticated, send the JWT. If guest, the browser sends the cookie automatically. Use `is_guest` in the response to decide whether to show a "Login to save your cart" prompt.
2. **Add to Cart (Guest):** Just call `POST /cart/items` normally. The browser will automatically store and re-send the `guest_cart_token` HttpOnly cookie on all future requests.
3. **On Login:** After receiving the JWT, no extra merge call is needed. The backend handles merge internally. Just refetch `GET /cart/` to get the merged cart state.
4. **Optimistic Updates:** Update the UI immediately on add/update. Revert if the server returns `INSUFFICIENT_STOCK`.
5. **Cart Badge:** Use `total_quantity` from `GET /cart/` for the header badge count.
6. **Product Thumbnails:** Use the `thumbnail` field in each cart item for the cart drawer/sidebar list.
