# Marketing and Sale Campaign Studio Documentation

## Overview
The Marketing Studio allows admins to create and manage time-limited promotions, discount campaigns, and featured banners. The system supports both explicit product selection and rule-based targeting for massive scalability.

---

## Promotion & Campaign Scopes

A **Promotion** represents a marketing event (e.g., "Dashain Sale" or "Summer Collection").

**Fields:** `id`, `title`, `description`, `image`, `cta_text`, `cta_link`, `is_active`, `sort_order`.

### Targeting Scopes (Rule-Based)
To support large-scale campaigns, Promotions can target products via three mechanisms:

1.  **Explicit Selection (`products`)**: A hard-linked list of specific products. Best for small, curated highlights.
2.  **Category Scope (`category`)**: Targets an entire category. When the Storefront API loads this promotion, it automatically includes all active products from this category.
3.  **Brand Scope (`brand`)**: Targets all products from a specific brand.

> [!TIP]
> **Priority**: If a promotion has both a category and explicit products, the API merges them and returns a unique, deduplicated list of products.

---

## Campaign API

### Backoffice Endpoints (Admin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/backoffice/cms/promotions` | List all promotions |
| GET | `/api/v1/backoffice/products/ids` | Bulk ID fetcher (for mass selection) |
| GET | `/api/v1/backoffice/brands` | Brand metadata |
| GET | `/api/v1/backoffice/cms/collections` | Section metadata |

### Storefront Endpoints (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/storefront/promotions` | List active campaigns with their targeted products |

---

## Studio Workflow

1.  **Filtering**: Use the advanced filters on `/backoffice/products` to find the target audience (e.g., "All Cotton Kurtis under 2000").
2.  **Assignment**: 
    - For small lists: Select individual products and send `product_ids`.
    - For large groups: Choose the entire Category or Brand in the Campaign Studio settings.
3.  **Exclusion**: To hide a campaign temporarily without deleting it, toggle `is_active` to `False`.
