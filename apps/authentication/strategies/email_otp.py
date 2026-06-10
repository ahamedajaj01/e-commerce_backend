from .base import BaseAuthStrategy
from ..services.otp_service import OTPService
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOTPStrategy(BaseAuthStrategy):
    def __init__(self, otp_service: OTPService):
        self.otp_service = otp_service
        
    def authenticate(self, credentials: dict):
        email = credentials.get('email')
        code = credentials.get('otp')
        
        if not email or not code:
            return None
            
        if self.otp_service.verify_otp(destination=email, code=code, purpose='LOGIN'):
            try:
                user = User.objects.get(email=email, is_email_verified=True, is_active=True)
                return user
            except User.DoesNotExist:
                return None
        return None
