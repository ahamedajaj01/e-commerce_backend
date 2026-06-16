"""
Production-grade password management service.

Handles:
  - Authenticated password change (old + new password)
  - Forgot password flow (OTP-based reset)
"""

import uuid
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .otp_service import OTPService

User = get_user_model()

PASSWORD_RESET_PURPOSE = 'PASSWORD_RESET'


class PasswordService:
    def __init__(self, otp_service: OTPService):
        self.otp_service = otp_service

    # ──────────────────────────────────────────────
    # 1. CHANGE PASSWORD (Authenticated)
    # ──────────────────────────────────────────────
    def change_password(self, user, old_password: str, new_password: str) -> dict:
        """
        Change password for an authenticated user.
        Returns dict with 'success' bool and 'message' str.
        """
        # Verify old password
        if not user.check_password(old_password):
            return {'success': False, 'message': 'Current password is incorrect.'}

        # Don't allow same password
        if old_password == new_password:
            return {'success': False, 'message': 'New password must be different from the current password.'}

        # Validate new password against Django's password validators
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return {'success': False, 'message': ' '.join(e.messages)}

        user.set_password(new_password)
        user.save(update_fields=['password'])
        return {'success': True, 'message': 'Password changed successfully.'}

    # ──────────────────────────────────────────────
    # 2. FORGOT PASSWORD — Request OTP
    # ──────────────────────────────────────────────
    def request_password_reset(self, email: str) -> dict:
        """
        Send a password reset OTP to the user's email.
        Always returns success to prevent email enumeration attacks.
        """
        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            # Respond with success to prevent email enumeration
            return {'success': True, 'message': 'If an account exists with this email, a reset code has been sent.'}

        sent = self.otp_service.create_and_send_otp(
            destination=email,
            purpose=PASSWORD_RESET_PURPOSE
        )

        if not sent:
            return {'success': False, 'message': 'Failed to send reset code. Please try again later.'}

        return {'success': True, 'message': 'If an account exists with this email, a reset code has been sent.'}

    # ──────────────────────────────────────────────
    # 3. VERIFY RESET OTP
    # ──────────────────────────────────────────────
    def verify_reset_otp(self, email: str, code: str) -> dict:
        """
        Verify the OTP and return a one-time reset token.
        """
        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            return {'success': False, 'message': 'Invalid email address.', 'reset_token': None}

        is_valid = self.otp_service.verify_otp(
            destination=email,
            code=code,
            purpose=PASSWORD_RESET_PURPOSE
        )

        if not is_valid:
            return {'success': False, 'message': 'Invalid or expired reset code.', 'reset_token': None}

        # Generate a secure one-time reset token in DB
        from ..models.password_reset import PasswordResetToken
        reset_token_obj = PasswordResetToken.create_for_user(user)

        return {'success': True, 'message': 'Code verified successfully.', 'reset_token': reset_token_obj.token}

    # ──────────────────────────────────────────────
    # 4. RESET PASSWORD (with token)
    # ──────────────────────────────────────────────
    def reset_password(self, reset_token: str, new_password: str) -> dict:
        """
        Set a new password using the verified reset token.
        """
        from ..models.password_reset import PasswordResetToken
        
        try:
            token_obj = PasswordResetToken.objects.get(token=reset_token)
        except PasswordResetToken.DoesNotExist:
            return {'success': False, 'message': 'Invalid or expired reset token. Please request a new code.'}

        if not token_obj.is_valid():
            return {'success': False, 'message': 'Reset token has expired or already been used.'}

        user = token_obj.user

        # Validate new password
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return {'success': False, 'message': ' '.join(e.messages)}

        user.set_password(new_password)
        user.save(update_fields=['password'])

        # Invalidate the token immediately so it can't be reused
        token_obj.is_used = True
        token_obj.save()

        return {'success': True, 'message': 'Password has been reset successfully. You can now log in.'}
