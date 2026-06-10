from django.db import models
from django.utils import timezone

class OTP(models.Model):
    destination = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=50) # e.g. 'SIGNUP'
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.purpose} OTP for {self.destination}"
