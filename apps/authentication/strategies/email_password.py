from .base import BaseAuthStrategy
from django.contrib.auth import authenticate

class EmailPasswordStrategy(BaseAuthStrategy):
    def authenticate(self, credentials: dict):
        email = credentials.get('email')
        password = credentials.get('password')
        
        if not email or not password:
            return None
            
        # Using the standard backend which we configured to accept username=email
        user = authenticate(username=email, password=password)
        if user and getattr(user, 'is_email_verified', False):
            return user
        return None
