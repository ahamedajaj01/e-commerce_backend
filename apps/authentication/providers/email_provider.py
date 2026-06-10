from .base import BaseOTPProvider
from django.core.mail import send_mail
from django.conf import settings

class EmailOTPProvider(BaseOTPProvider):
    def send_otp(self, destination: str, code: str, purpose: str = 'verification') -> bool:
        subject = "Your Verification Code"
        message = f"Your Verification code is: {code}.\nPlease do not share this with anyone."
        
        try:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                [destination],
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Here we might log the exception securely
            return False
