# Shipping & Delivery Management Documentation

## Overview
The shipping system uses a **flat, hierarchical rule table** (`ShippingRule`) that works directly with the structured address data returned by Google Places Autocomplete.

Effective Phase 1, the architecture strictly separates **Transit Time** (location-based) from **Fulfillment/Processing Time** (product-based) to ensure clean separation of responsibilities between shipping and catalog domains.

---

## Key Concepts

1. **Shipping Rule:** A single database row that defines a fee and transit time for a specific geographic scope.
2. **Transit Time (Shipping Concern):** The number of days a courier takes to deliver from the warehouse to the destination.
3. **Product Processing Time (Catalog Concern):** The number of days required to prepare a specific product before it can be handed to a courier.
4. **Checkout Layer (Coordination Concern):** The layer responsible for summing both components to generate the final customer-facing estimate.

---

## Shipping Rule Hierarchy
Matching stops at the **first valid rule found**, proceeding from most-specific to most-general (Province + District + City -> Province + District -> Province -> Default).

| Priority | Level | Fee | Example Transit |
|----------|-------|-----|-----------------|
| **1** | City | Lowest | 1-2 Days |
| **2** | District | Medium | 2-3 Days |
| **3** | Province | High | 3-5 Days |
| **4** | Default | Highest | 5-7 Days |

---

## Storefront API

### POST /api/v1/storefront/shipping/calculate/
Calculates the shipping fee and provides granular **Transit Time** data.

- **Note on Responsibility:** This endpoint returns data strictly about the **courier's journey**. It does NOT include product preparation time.
- **Success Response:**
  ```json
  {
    "success": true,
    "data": {
      "rule_id": "uuid",
      "fee": 100.00,
      "estimated_days": "2-3 Business Days",
      "transit_days_min": 2,
      "transit_days_max": 3
    }
  }
  ```

---

## Architectural Responsibility: Delivery Estimation

To ensure the system remains maintainable, the estimation logic is split across three layers:

### 1. Shipping Layer (Transit)
Responsible for identifying how long the package stays in the courier's truck. 
- **Fields:** `transit_days_min`, `transit_days_max`.
- **API:** Returns these values based on the matched location.

### 2. Catalog Layer (Preparation)
Responsible for identifying how long the item stays in the warehouse.
- **Fields:** `processing_days_min`, `processing_days_max`.
- **Logic:** Defined per product. Custom orders or supplier-fulfilled items will have higher values.

### 3. Checkout Layer (Aggregation)
Responsible for the final math. This layer (or the Frontend Integration) combines the components:

**The Formula:**
`Total Min Days = Max(Items in Cart Processing Min) + Shipping Transit Min`
`Total Max Days = Max(Items in Cart Processing Max) + Shipping Transit Max`

---

## Admin Panel (Backoffice)
Ensure that:
1. **Logistics Admins** only manage `transit_days` (Courier rates/times).
2. **Catalog Admins** only manage `processing_days` (Product lead times).

---

## Google Places Integration Guide
1. **Extraction:**
   - `administrative_area_level_1` → `province`
   - `administrative_area_level_2` → `district`
   - `locality` → `city`
2. **Error Handling:** `404` indicates shipping is unavailable. Always display the returned `fee` and use the transit days to calculate the final delivery promise.
