from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SendOTPSerializer, VerifyOTPSerializer, CompleteSignupSerializer
from ..services.signup_service import SignupService
from ..services.otp_service import OTPService
from ..providers.email_provider import EmailOTPProvider

def get_signup_service():
    provider = EmailOTPProvider()
    otp_service = OTPService(provider)
    return SignupService(otp_service)


class SendOTPView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            service = get_signup_service()
            success = service.initiate_signup(email=serializer.validated_data['email'])
            
            if success:
                return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "Failed to send OTP or email already registered."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            service = get_signup_service()
            token = service.verify_signup_otp(
                email=serializer.validated_data['email'],
                code=serializer.validated_data['otp']
            )
            
            if token:
                return Response({"signup_token": token}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteSignupView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = CompleteSignupSerializer(data=request.data)
        if serializer.is_valid():
            service = get_signup_service()
            user = service.complete_signup(
                token=serializer.validated_data['signup_token'],
                password=serializer.validated_data['password']
            )
            
            if user:
                return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
            return Response({"error": "Invalid token or token expired."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
