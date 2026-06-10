from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

class PendingRegistration(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    verification_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_token_valid(self):
        return self.is_verified and self.verification_token and self.token_expires_at > timezone.now()

    def __str__(self):
        return f"Pending Registration: {self.email}"
