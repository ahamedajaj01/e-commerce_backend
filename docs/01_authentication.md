# Authentication and OTP System Documentation

## Overview
The platform implements a secure, multi-step email-based authentication system. It uses a Pending Registration pattern to ensure only verified emails can create accounts.

## Authentication Flow

### 1. Request OTP
Initiates the signup process by sending a 6-digit code to the user's email.
- **Endpoint:** `POST /api/v1/auth/signup/send-otp/`
- **Payload:**
  ```json
  {
      "email": "user@example.com"
  }
  ```
- **Logic:** Creates a `PendingRegistration` record. Codes expire after 10 minutes.

### 2. Verify OTP
Verifies the code and returns a temporary verification token.
- **Endpoint:** `POST /api/v1/auth/signup/verify-otp/`
- **Payload:**
  ```json
  {
      "email": "user@example.com",
      "otp": "123456"
  }
  ```
- **Response:** Returns `signup_token` (valid for 1 hour).

### 3. Complete Signup
Finalizes account creation with a password.
- **Endpoint:** `POST /api/v1/auth/signup/complete/`
- **Payload:**
  ```json
  {
      "signup_token": "uuid-token-from-step-2",
      "password": "securepassword123"
  }
  ```

### 4. Login
Standard email and password login.
- **Endpoint:** `POST /api/v1/auth/login/`
- **Payload:**
  ```json
  {
      "email": "user@example.com",
      "password": "securepassword123"
  }
  ```
- **Response:** JWT access token, refresh token, and nested `user` profile data.

### 5. Current User Profile
Retrieves the profile of the currently authenticated user.
- **Endpoints:** 
  - `GET /api/v1/auth/users/me/`
  - `GET /api/v1/auth/profile/`
- **Requirement:** Must include `Authorization: Bearer <access_token>` header.
- **Data returned:** `id`, `email`, `role`, `is_staff`, `is_email_verified`, etc.

## Frontend Integration Guide

1. **State Management:** Store the `email` during the OTP step and the `signup_token` during the verification step.
2. **Post-Login:** On a successful login, the API returns the user object immediately. Store this in your Global State (Redux/Zustand) to avoid extra API calls.
3. **Session Rehydration:** If the user refreshes the page, call `GET /api/v1/auth/users/me/` using the stored token to verify the session and restore user info.
4. **Error Handling:** Catch 400 errors for "Invalid OTP" or "Expired OTP" and 401 for "Invalid Credentials".
5. **Security:** Store the `access` token in memory or secure storage for all subsequent API requests. Include it in the `Authorization: Bearer <token>` header.

---

## Password Management

### 1. Change Password (Authenticated)
Allows a logged-in user to change their password.
- **Endpoint:** `POST /api/v1/auth/password/change/`
- **Requires:** `Authorization: Bearer <token>`
- **Payload:**
  ```json
  {
      "old_password": "currentPassword123",
      "new_password": "newSecurePassword456"
  }
  ```
- **Validation:** Django's built-in password validators enforce minimum length, common password checks, and similarity to user attributes.
- **Error Cases:** Wrong old password, same old/new password, weak new password.

### 2. Forgot Password — Request OTP
Sends a 6-digit reset code to the user's email. Always returns `200` to prevent email enumeration attacks.
- **Endpoint:** `POST /api/v1/auth/password/forgot/`
- **Requires:** Public (no auth)
- **Payload:**
  ```json
  {
      "email": "user@example.com"
  }
  ```

### 3. Verify Reset OTP
Verifies the reset code and returns a one-time `reset_token` (valid for 15 minutes).
- **Endpoint:** `POST /api/v1/auth/password/verify-otp/`
- **Requires:** Public (no auth)
- **Payload:**
  ```json
  {
      "email": "user@example.com",
      "otp": "123456"
  }
  ```
- **Response:**
  ```json
  {
      "success": true,
      "message": "Code verified successfully.",
      "data": { "reset_token": "uuid-token" }
  }
  ```

### 4. Reset Password
Sets a new password using the verified reset token.
- **Endpoint:** `POST /api/v1/auth/password/reset/`
- **Requires:** Public (no auth)
- **Payload:**
  ```json
  {
      "reset_token": "uuid-token-from-step-3",
      "new_password": "newSecurePassword456"
  }
  ```
- **Security:** Token is single-use and auto-expires after 15 minutes.

### Frontend Password Reset Flow
1. User clicks "Forgot Password" → call `POST /auth/password/forgot/` with their email.
2. User enters the OTP from their email → call `POST /auth/password/verify-otp/`.
3. Store the returned `reset_token` in component state.
4. User enters new password → call `POST /auth/password/reset/` with the token.
5. On success, redirect to the login page.
