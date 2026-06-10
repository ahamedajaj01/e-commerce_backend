from django.db import models
from core.common.models.base import BaseModel

class NavigationMenu(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title
