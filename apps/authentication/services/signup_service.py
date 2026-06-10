import uuid
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from ..models.pending_registration import PendingRegistration
from .otp_service import OTPService

User = get_user_model()

class SignupService:
    def __init__(self, otp_service: OTPService):
        self.otp_service = otp_service
    
    def initiate_signup(self, email: str) -> bool:
        if User.objects.filter(email=email).exists():
            return False
            
        pending, _ = PendingRegistration.objects.get_or_create(email=email)
        
        # Reset if needed
        pending.is_verified = False
        pending.verification_token = None
        pending.save()
        
        return self.otp_service.create_and_send_otp(destination=email, purpose='SIGNUP')
        
    def verify_signup_otp(self, email: str, code: str) -> str:
        try:
            pending = PendingRegistration.objects.get(email=email)
        except PendingRegistration.DoesNotExist:
            return None
            
        is_valid = self.otp_service.verify_otp(destination=email, code=code, purpose='SIGNUP')
        if not is_valid:
            return None
            
        pending.is_verified = True
        pending.verification_token = str(uuid.uuid4())
        pending.token_expires_at = timezone.now() + timedelta(hours=1)
        pending.save()
        
        return pending.verification_token
        
    def complete_signup(self, token: str, password: str) -> User:
        try:
            pending = PendingRegistration.objects.get(verification_token=token)
        except PendingRegistration.DoesNotExist:
            return None
            
        if not pending.is_token_valid():
            return None
            
        user = User.objects.create_user(
            email=pending.email,
            password=password,
            is_email_verified=True
        )
        
        pending.delete()
        return user
