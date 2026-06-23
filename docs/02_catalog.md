# Catalog and Product System Documentation

## Overview
The catalog domain manages the lifecycle of categories, products, and their variants. It follows a fashion-first architecture where inventory and pricing are tied to specific variants (Size/Color).

---

## Category
**Fields:** `id`, `name`, `slug`, `parent`, `children`, `is_active`.

---

## Product
The base conceptual entity for a sellable item. 

**Core Fields:** `id`, `name`, `slug`, `brand`, `description`, `base_price`, `category`.

**Design Attributes:** `material`, `sleeve`, `length`, `neck_line`, `fit`.

**Logistics Metadata:**
- **`processing_days_min`**: Minimum days to prepare the product for shipping (default: 0).
- **`processing_days_max`**: Maximum days to prepare the product for shipping (default: 0).
  > These are used by the [Shipping System](./05_shipping_delivery.md) to calculate order-level delivery estimates.

**Visibility:**
- `is_featured`: Best Sellers/Homepage.
- `is_new`: New Arrivals.
- `is_trending`: Trending items.
- `is_active`: Published status.
- `is_visible`: Toggle to hide from main store search/grid while keeping it purchasable via direct link or campaigns.

---

### Storefront API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/storefront/products` | List all active products |
| GET | `/api/v1/storefront/products/{slug}` | Get product detail |

---

### Backoffice API (Requires Staff role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/backoffice/products` | Paginated list with filters |
| POST | `/api/v1/backoffice/products` | Create product (includes Variants & Media) |

**Create / Edit Payload (multipart/form-data):**
```text
name: Silk Sari
category_id: 1
processing_days_min: 1
processing_days_max: 2
image: <File>
...
variants: [{"sku": "SKU-1", "price": 2500, "size": "L", "color": "Red", "stock_quantity": 50}]
```

---

## Product Variant
The specific purchasable unit (e.g., "Red / XL").
**Fields:** `id`, `sku`, `size`, `color`, `price`, `stock_quantity`, `is_unlimited_stock`.

---

## Product Media
**Fields:** `id`, `media_type` (IMAGE), `file`, `file_url` (absolute), `sort_order`, `alt_text`.

---

## Frontend Integration Guide

1. **Fulfillment Info:** Use `processing_days_min/max` from the product detail response to show "Dispatches in X days" on the product detail page.
2. **Variants:** All cart operations strictly require the `variant.id`.
3. **Gallery:** The `media` array is sorted by `sort_order`. `media[0]` is the primary thumbnail.
