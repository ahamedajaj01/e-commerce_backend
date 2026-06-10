# Shipping & Delivery Management Documentation

## Overview
The shipping system uses a **flat, hierarchical rule table** (`ShippingRule`) that works directly with the structured address data returned by Google Places Autocomplete.

It supports future courier API integrations via the **Provider Strategy Pattern** (see bottom of this doc) while keeping the storefront API stable.

---

## Key Concepts

1. **Shipping Rule:** A single database row that defines a fee for a specific geographic scope.
2. **Hierarchical Matching:** The backend finds the most specific applicable rule automatically — no neighborhood-level entries required from the admin.
3. **Google Places Normalizer:** The backend strips common Google suffixes (e.g. "Province", "Metropolitan City") before matching, so admin doesn't need to replicate Google's naming conventions.
4. **Default Rule:** One rule may be marked `is_default=True` to act as a nationwide fallback for unrecognized addresses.

---

## Shipping Rule Hierarchy

Matching stops at the **first valid rule found**, proceeding from most-specific to most-general:

| Priority | Pattern | Example Config | Fee |
|----------|---------|----------------|-----|
| **1** | Province + District + City | Bagmati / Kathmandu / Kathmandu Metropolitan | NPR 100 |
| **2** | Province + District | Bagmati / Kathmandu | NPR 150 |
| **3** | Province only | Bagmati | NPR 200 |
| **4** | Default (nationwide) | `is_default=True` | NPR 300 |

> **Admin note:** Never create neighborhood-level rules (Anamnagar, Baneshwor, Kalanki). Those addresses will automatically fall under the district or province rule.

---

## Storefront API

### POST /api/v1/storefront/shipping/calculate/

After the user selects an address via Google Places Autocomplete, the frontend extracts the structured `province`, `district`, and `city` fields from the geocode result and sends them here.

- **Auth:** Optional (works for guests too)
- **Payload:**
  ```json
  {
    "province": "Bagmati",
    "district": "Kathmandu",
    "city": "Kathmandu",
    "order_total": 2500.00
  }
  ```
  > All geo fields are optional. The backend will match whatever is provided, falling back to broader rules if needed.

- **Success Response:**
  ```json
  {
    "success": true,
    "data": {
      "rule_id": "c1a2b3d4-5678-90ab-cdef-1234567890ab",
      "title": "Bagmati + Kathmandu + Kathmandu Metropolitan",
      "fee": 100.00,
      "estimated_days": "2-3 Business Days"
    }
  }
  ```

- **Error Response (no matching rule):**
  ```json
  {
    "success": false,
    "message": "Shipping is currently not available for this location."
  }
  ```
  HTTP status: **404**

---

## Backoffice API (Admin)

### 1. List / Create Shipping Rules

- **List:** `GET /api/v1/backoffice/shipping/rules/`
- **Create:** `POST /api/v1/backoffice/shipping/rules/`

**Create Payload:**
```json
{
  "title": "Bagmati + Kathmandu + Kathmandu Metropolitan",
  "province": "Bagmati",
  "district": "Kathmandu",
  "city_or_municipality": "Kathmandu",
  "shipping_fee": 100.00,
  "estimated_days": "2-3 Business Days",
  "is_default": false,
  "is_active": true
}
```

**Create a Default (Nationwide) Rule:**
```json
{
  "title": "Default Nationwide",
  "shipping_fee": 300.00,
  "estimated_days": "7-10 Business Days",
  "is_default": true,
  "is_active": true
}
```
> Only **one** default rule is allowed. The serializer will reject a second default.

---

### 2. Retrieve / Update / Delete Rule

- **Retrieve:** `GET /api/v1/backoffice/shipping/rules/{id}/`
- **Update:** `PATCH /api/v1/backoffice/shipping/rules/{id}/`
- **Delete:** `DELETE /api/v1/backoffice/shipping/rules/{id}/`

---

### 3. Toggle Rule Activation

- **Endpoint:** `POST /api/v1/backoffice/shipping/rules/{id}/toggle/`
- **Purpose:** Quickly enable/disable a rule (e.g. disable a province during a delivery strike) without editing the full payload.
- **Response:**
  ```json
  {
    "success": true,
    "data": { "id": "uuid", "is_active": false },
    "message": "Rule deactivated successfully"
  }
  ```

---

## Business Logic & Rules

1. **Google Places Normalization:** Before matching, the backend strips suffixes like `Province`, `Metropolitan City`, `Municipality`, `Sub-Metropolitan`, etc. from all incoming address strings so they match clean admin-entered names.

2. **Hierarchical Matching:** First match wins:
   - Province + District + City
   - Province + District
   - Province only
   - Default (`is_default=True`)

3. **No Match:** If no rule applies, the API returns a `404` — the frontend should display "Shipping is currently not available for this location."

4. **Snapshotting (future Orders module):** Once a fee is selected at checkout, it will be snapshotted onto the `Order` record. Future admin price changes will **not** affect historical orders.

---

## Frontend Integration Guide

1. **Single Address Input:** Use a **Google Places Autocomplete** text field (not dropdowns). Let the user type any address; Google handles suggestions.

2. **Extract Fields:** When the user picks a suggestion, use the Google Places result to extract:
   - `administrative_area_level_1` → `province`
   - `administrative_area_level_2` → `district`
   - `locality` → `city`

3. **Calculate Fee:** Silently post the extracted values to `POST /api/v1/storefront/shipping/calculate/` and display the returned fee.

4. **Delivery Instructions:** Hold the user's free-text "Additional Context / Landmark" in frontend state. It will be posted to `POST /api/v1/orders/` as `delivery_instructions` when the Orders module is ready.

5. **Error Handling:**
   - `404` → Show "We currently do not deliver to this location."
   - `400` → Show "Invalid address data, please try again."

---

## Future: Adding Courier APIs (Pathao, Aramex, etc.)

The `ShippingProvider` model already has `provider_type` (`MANUAL` or `API`) and a JSON `configuration` column for storing API keys.

### How to Implement:

1. **Save credentials** in the `ShippingProvider` table via the Admin UI (add a "Couriers" screen to Logistics Studio).
2. **Create a new class** in `apps/shipping/services/shipping_service.py` (e.g. `PathaoShippingProvider`) that fetches live rates from the courier's API.
3. **Register it** in `ShippingService.get_provider()`.
4. **No storefront changes needed** — the `POST /shipping/calculate/` endpoint signature stays identical.
