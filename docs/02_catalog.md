# Catalog and Product System Documentation

## Overview
The catalog domain manages the lifecycle of categories, products, and their variants. It follows a fashion-first architecture where inventory and pricing are tied to specific variants (Size/Color).

---

## Category

Supports a nested parent-child hierarchy to organize fashion items (e.g., `Women` > `Kurti` > `Printed`).

**Fields:** `id`, `name`, `slug` (auto-generated), `parent`, `children`, `is_active`.

---

## Brand
Manages brand identities for products.

**Fields:** `id`, `name`, `slug`, `logo`, `description`, `is_active`.

### Backoffice API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/backoffice/brands` | List all brands |
| POST | `/api/v1/backoffice/brands` | Create a brand |

### Storefront API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/storefront/categories` | List all active categories |

### Backoffice API (Requires Staff role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/backoffice/categories` | List all categories |
| POST | `/api/v1/backoffice/categories` | Create a new category |
| PATCH | `/api/v1/backoffice/categories/{id}` | Edit a category |
| DELETE | `/api/v1/backoffice/categories/{id}` | Delete a category |

**Create Payload:**
```json
{
    "name": "Ladies Kurti",
    "parent_id": null
}
```

**Notes:**
- The `slug` is automatically generated from the `name`. Duplicates are handled gracefully (e.g., `ladies-kurti`, `ladies-kurti-1`).
- To create a subcategory, provide a valid `parent_id`.

---

## Product

The base conceptual entity for a sellable item. Products hold the general information. Actual stock and pricing live in Variants.

**Fields:** `id`, `name`, `slug`, `brand`, `description`, `base_price`, `category`, `material`, `sleeve`, `length`, `neck_line`, `fit`, `is_featured`, `is_new`, `is_trending`, `is_active`, `is_visible`, `variants`, `media`.

### Backoffice Filtering & Search
The Backoffice product list supports advanced filtering for bulk operations and studio management.

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search by name, SKU, or brand name |
| `category` | UUID | Filter by specific category ID |
| `brand` | UUID | Filter by specific brand ID |
| `min_price` | decimal | Minimum base price |
| `max_price` | decimal | Maximum base price |
| `stock_status` | enum | `in_stock` or `out_of_stock` |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Results per page (default: 20) |

#### Product Visibility Override (Exclusive Collections)
- **`is_visible`**: A toggle to hide products from the main store or site search. If set to `False` (Hidden), the product is excluded from general discovery but can still be manually assigned to exclusive Homepage Collections or Promotional Campaigns and remains fully purchasable.

#### Newly Added Design Attributes
The `Product` model natively stores apparel constraints out of the box:
- **`material`**: E.g., "Georgette", "Cotton"
- **`sleeve`**: E.g., "Flutter sleeves", "Full sleeve"
- **`length`**: E.g., "Under Bust", "Ankle"
- **`neck_line`**: E.g., "V-Neck", "Round"
- **`fit`**: E.g., "Regular", "Slim"

### Storefront API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/storefront/products` | List all active products with variants and media |
| GET | `/api/v1/storefront/products/{slug}` | Get detail of a specific product by slug |
| GET | `/api/v1/storefront/products?category={id}` | Filter products by category ID (includes subcategories) |
| GET | `/api/v1/storefront/products?category_slug={slug}` | Filter products by category slug (includes subcategories) |
| GET | `/api/v1/storefront/products?search=kurti` | Search products by name or description |
| GET | `/api/v1/storefront/products?is_featured=true` | List featured products (used for Best Sellers) |
| GET | `/api/v1/storefront/products?is_new=true` | List newly arrived products |
| GET | `/api/v1/storefront/products?is_trending=true` | List trending products |

### Backoffice API (Requires Staff role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/backoffice/products` | Paginated product list with filters |
| GET | `/api/v1/backoffice/products/ids` | List of UUIDs matching current filters |
| POST | `/api/v1/backoffice/products` | Create a product |
| PATCH | `/api/v1/backoffice/products/{id}` | Edit a product |
| DELETE | `/api/v1/backoffice/products/{id}` | Delete a product |
| GET | `/api/v1/backoffice/cms/collections` | List active homepage sections/collections |

**Create / Edit Payload (multipart/form-data):**
```text
name: Silk Sari
description: Luxurious handwoven silk.
category_id: 1
material: Silk
fit: Regular
image: <File> (Main Thumbnail - Compulsory)
images: <File> (Gallery Image 1)
images: <File> (Gallery Image 2)
images: ...
variants: [{"sku": "SILK-RED-L", "price": 2500, "size": "L", "color": "Red", "stock_quantity": 50, "is_unlimited_stock": false}]
```

**Admin Product Variants Architecture (Sync & Writable Nested)**
The `POST` and `PATCH` endpoints for products are designed to handle complex variant synchronization via a JSON string under the `variants` form key:
- **POST (Creation):** Automatically creates all variants and sets their initial stock levels.
- **PATCH (Syncing Updates):** 
    - **Update Existing:** If a variant dictionary includes an `"id"`, the backend matches it to the product and updates its SKU, price, and attributes.
    - **Create New:** If a variant dictionary has NO `"id"`, the backend assumes it's a new option (e.g., adding a new color/size during an edit) and creates it.
    - **Stock Sync:** Initial `stock_quantity` can also be passed here to override the current ledger value.

---

## Product Variant

The specific purchasable unit of a product (e.g., "Red / XL"). All cart and order operations reference the Variant ID, not the Product ID.

**Fields:** `id`, `sku`, `size`, `color`, `price`, `stock_quantity`, `is_unlimited_stock`, `is_active`.

*Note: `stock_quantity` and `is_unlimited_stock` are physically stored in the `Inventory` table but efficiently serialized directly inside the variant payload for easy frontend cart validation.*

---

## Product Media

Supports multiple image uploads to build rich product galleries natively.

**Fields:** `id`, `media_type` (IMAGE), `file` (relative), `file_url` (absolute), `sort_order`, `alt_text`.

**Storage:** Physical files are saved to `media/products/media/` on the server. The APIs automatically resolve and return the absolute `file_url`, resolving cross-origin pathing automatically.

---

## Frontend Integration Guide

1. **Category Manager:** Use `GET /backoffice/categories` to list, `POST` to create, `PATCH` to edit, and `DELETE` to remove. Use `parent_id` to build subcategory relationships.
2. **Category Navigation:** For primary storefront navigation (top menus/sidebars), use the **CMS Navigation System** (see [CMS Documentation](./04_cms_discovery.md)). For simple flat lists or breadcrumbs, you can still use `GET /api/v1/storefront/categories`.
3. **Multi-Image Form Appending (Admin):** When creating or editing products, append the main photo as `image`, and loop all secondary photos appending them to the array key `images`.
4. **Product List/Grid:** Call `GET /api/v1/storefront/products` to populate product cards. The **first** object in the array `product.media[0].file_url` is guaranteed by the backend to be the primary thumbnail.
5. **Product Detail Page (The Gallery):** Use the `media` array to build the deep page layout! Render `media[0]` at the top, and loop `{product.media.slice(1).map(...)}` to render the remaining gallery shots below it.
6. **Variants:** Use the `variants` array to build size and color selectors. When the user selects a combination, store that specific `variant.id` and pass it to "Add to Cart".
