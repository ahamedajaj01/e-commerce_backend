from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    @classmethod
    def create_for_user(cls, user):
        # Invalidate existing tokens for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(minutes=15)
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    def __str__(self):
        return f"Reset token for {self.user.email}"
