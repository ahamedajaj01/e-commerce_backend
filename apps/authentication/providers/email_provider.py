from .base import BaseOTPProvider
from django.core.mail import send_mail
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

class EmailOTPProvider(BaseOTPProvider):
    def send_otp(self, destination: str, code: str, purpose: str = 'verification') -> bool:
        subject = "Your Verification Code"
        message = f"Your Verification code is: {code}.\nPlease do not share this with anyone."
        
        # Priority: Settings -> env -> fallback
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'onboarding@resend.dev')
        resend_api_key = getattr(settings, 'RESEND_API_KEY', None)
        
        if resend_api_key:
            try:
                import resend
                resend.api_key = resend_api_key
                logger.info(f"Attempting to send OTP via Resend to {destination}")
                resend.Emails.send({
                    "from": from_email,
                    "to": destination,
                    "subject": subject,
                    "text": message,
                })
                return True
            except Exception as e:
                logger.error(f"Resend OTP delivery failed to {destination}. Error: {str(e)}")
                # Continue to fallback if requested, but usually Resend failure 
                # means API key or domain issues
        
        # Fallback to standard Django send_mail (SMTP)
        try:
            logger.info(f"Attempting to send OTP via SMTP to {destination}")
            send_mail(
                subject,
                message,
                from_email,
                [destination],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"SMTP OTP delivery failed to {destination}. Error: {str(e)}")
            return False


