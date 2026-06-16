from django.db import models
from core.common.models.base import BaseModel

class Promotion(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cta_text = models.CharField(max_length=100, blank=True, help_text="Button label, e.g. 'Shop Now'")
    cta_link = models.CharField(max_length=500, blank=True, help_text="Redirect URL for the CTA button")
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='cms/promotions/', null=True, blank=True)
    category = models.ForeignKey(
        'catalog.Category',
        on_delete=models.SET_NULL,
        related_name='promotions',
        null=True,
        blank=True
    )
    brand = models.ForeignKey(
        'catalog.Brand',
        on_delete=models.SET_NULL,
        related_name='promotions',
        null=True,
        blank=True
    )
    products = models.ManyToManyField(
        'catalog.Product',
        related_name='promotions',
        blank=True
    )
    TYPE_CHOICES = (
        ('BANNER', 'Visual Banner'),
        ('CAMPAIGN', 'Marketing Campaign'),
        ('EXCLUSIVE', 'System Exclusive'),
    )
    promotion_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='CAMPAIGN')
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title
