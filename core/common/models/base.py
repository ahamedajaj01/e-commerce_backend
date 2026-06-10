import uuid
from django.db import models

class UUIDModel(models.Model):
    """Base model using UUID as primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class TimeStampedModel(models.Model):
    """Base model with created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BaseModel(UUIDModel, TimeStampedModel):
    """Combined base model with UUID and timestamps."""
    class Meta:
        abstract = True
