from ..strategies.base import BaseAuthStrategy
from django.contrib.auth import get_user_model

class AuthService:
    def __init__(self, strategy: BaseAuthStrategy):
        self.strategy = strategy
        
    def authenticate(self, credentials: dict):
        return self.strategy.authenticate(credentials)
