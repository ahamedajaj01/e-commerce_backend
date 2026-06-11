import requests
from .base import BaseOTPProvider
from django.core.mail import send_mail
from django.conf import settings

class EmailOTPProvider(BaseOTPProvider):
    def send_otp(self, destination: str, code: str, purpose: str = 'verification') -> bool:
        subject = "Your Verification Code"
        message = f"Your Verification code is: {code}.\nPlease do not share this with anyone."
        provider = getattr(settings, 'EMAIL_PROVIDER', 'smtp').lower()

        if provider == 'sendcorex':
            return self._send_sendcorex_email(destination, subject, message)

        try:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                [destination],
                fail_silently=False,
            )
            return True
        except Exception:
            return False

    def _send_sendcorex_email(self, destination: str, subject: str, message: str) -> bool:
        api_url = getattr(settings, 'SENDCOREZX_API_URL', '')
        api_key = getattr(settings, 'SENDCOREZX_API_KEY', '')
        if not api_url or not api_key:
            return False

        payload = {
            'to': destination,
            'subject': subject,
            'message': message,
            'from': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            return response.ok
        except Exception:
            return False
