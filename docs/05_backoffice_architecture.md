# Platform Architecture and Role System Documentation

## Overview
The platform uses a modular domain architecture. Logic is split into Services (Business Actions) and Selectors (Data Retrieval). All operational access is controlled by a Staff Role system.

## Staff Roles
The current system defines the following operational roles:
- `admin`: Full platform access.
- `inventory`: Access to stock management and low-stock reports.
- `marketing`: Access to CMS and Banners.
- `support`: Access to orders and user inquiries (Operations).

## Operational Security

### Backoffice Namespace
All administrative APIs are grouped under `/api/v1/backoffice/`.

**Domain Groups:**
- **Storefront:** `/cms/` (Announcements, Navigation, Homepage)
- **Catalog:** `/products`, `/categories`
- **Inventory:** `/inventory/`

### Permissions
Access is enforced by the `IsBackofficeStaff` permission class.
- **Rules:** Users must have `is_staff=True` AND a non-null `role` to access protected operational endpoints.

## Global API Standards

### Success Response Format
```json
{
    "success": true,
    "message": "Step successful",
    "data": { ... }
}
```

### Error Response Format
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable explanation"
    }
}
```

## Maintenance Guide

1. **New Services:** Always place business transactions inside `services/` and wrap with `@transaction.atomic`.
2. **New Queries:** Use `selectors/` to prefetch related data (Categories, Media) to avoid N+1 query performance issues.
3. **Primary Keys:** Use the provided `BaseModel` (UUID-based) for all new domain models for distributed scalability.
