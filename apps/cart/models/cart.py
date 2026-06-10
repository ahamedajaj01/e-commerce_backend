import uuid as uuid_lib
from django.db import models
from django.conf import settings
from django.utils import timezone
from core.common.models.base import BaseModel


class Cart(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CHECKED_OUT = "CHECKED_OUT", "Checked Out"
        EXPIRED = "EXPIRED", "Expired"
        MERGED = "MERGED", "Merged"
        ABANDONED = "ABANDONED", "Abandoned"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True
    )
    # Guest cart token — unique, set only for anonymous carts
    guest_token = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )
    # Auto-expiry for guest carts (set to 30 days from creation)
    expires_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_guest(self):
        return self.user_id is None

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def __str__(self):
        if self.user:
            return f"Cart (User: {self.user}) - {self.id}"
        return f"Cart (Guest: {self.guest_token}) - {self.id}"
