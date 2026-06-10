from django.db import models
from core.common.models.base import BaseModel

class AnnouncementBar(BaseModel):
    title = models.CharField(max_length=255)
    cta_text = models.CharField(max_length=100, blank=True)
    redirect_url = models.CharField(max_length=500, blank=True)
    linked_product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements'
    )
    linked_promotion = models.ForeignKey(
        'cms.Promotion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements'
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title
