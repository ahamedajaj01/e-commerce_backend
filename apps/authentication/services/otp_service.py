import string
import secrets
from django.utils import timezone
from datetime import timedelta
from ..models.otp import OTP
from ..providers.base import BaseOTPProvider

class OTPService:
    def __init__(self, provider: BaseOTPProvider):
        self.provider = provider
        self.otp_length = 6
        self.expiry_minutes = 10

    def generate_code(self) -> str:
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(self.otp_length))

    def create_and_send_otp(self, destination: str, purpose: str) -> bool:
        # Delete any previous active OTPs for this destination/purpose before sending a new one
        OTP.objects.filter(destination=destination, purpose=purpose).delete()
        
        code = self.generate_code()
        expires_at = timezone.now() + timedelta(minutes=self.expiry_minutes)
        
        OTP.objects.create(
            destination=destination,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )
        
        return self.provider.send_otp(destination, code, purpose)
        
    def verify_otp(self, destination: str, code: str, purpose: str) -> bool:
        try:
            # We filter by created_at in descending order to always get the latest code.
            otp = OTP.objects.filter(
                destination=destination, 
                purpose=purpose, 
                code=code,
                is_used=False
            ).first()
            
            if not otp:
                return False
            
            if otp.is_valid():
                otp.delete()  # Instantly delete the OTP record once verified
                return True
                
            otp.attempt_count += 1
            otp.save()
            return False
            
        except Exception:
            return False
