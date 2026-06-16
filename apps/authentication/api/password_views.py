"""
Password management views.

Endpoints:
  POST /auth/password/change/      — Authenticated user changes password
  POST /auth/password/forgot/      — Request password reset OTP
  POST /auth/password/verify-otp/  — Verify reset OTP, get reset token
  POST /auth/password/reset/       — Set new password with reset token
"""

from rest_framework.views import APIView
from rest_framework import status

from core.common.responses.formatters import success_response, error_response
from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    VerifyResetOTPSerializer,
    ResetPasswordSerializer
)
from ..services.password_service import PasswordService
from ..services.otp_service import OTPService
from ..providers.email_provider import EmailOTPProvider


def get_password_service():
    provider = EmailOTPProvider()
    otp_service = OTPService(provider)
    return PasswordService(otp_service)


class ChangePasswordView(APIView):
    """
    Authenticated user changes their own password.
    Requires: Authorization: Bearer <token>
    """

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Validation failed", data=serializer.errors)

        service = get_password_service()
        result = service.change_password(
            user=request.user,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password']
        )

        if result['success']:
            return success_response(message=result['message'])
        return error_response(message=result['message'], status_code=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """
    Public endpoint — send password reset OTP to email.
    Always returns 200 to prevent email enumeration.
    """
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Validation failed", data=serializer.errors)

        service = get_password_service()
        result = service.request_password_reset(
            email=serializer.validated_data['email']
        )

        # Always return 200 to prevent email enumeration
        return success_response(message=result['message'])


class VerifyResetOTPView(APIView):
    """
    Public endpoint — verify the reset OTP and receive a one-time reset token.
    """
    permission_classes = []

    def post(self, request):
        serializer = VerifyResetOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Validation failed", data=serializer.errors)

        service = get_password_service()
        result = service.verify_reset_otp(
            email=serializer.validated_data['email'],
            code=serializer.validated_data['otp']
        )

        if result['success']:
            return success_response(
                data={'reset_token': result['reset_token']},
                message=result['message']
            )
        return error_response(message=result['message'], status_code=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    Public endpoint — set a new password using the verified reset token.
    """
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Validation failed", data=serializer.errors)

        service = get_password_service()
        result = service.reset_password(
            reset_token=serializer.validated_data['reset_token'],
            new_password=serializer.validated_data['new_password']
        )

        if result['success']:
            return success_response(message=result['message'])
        return error_response(message=result['message'], status_code=status.HTTP_400_BAD_REQUEST)
