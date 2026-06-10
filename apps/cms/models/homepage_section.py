from django.db import models
from core.common.models.base import BaseModel

class HomepageSection(BaseModel):
    class SectionType(models.TextChoices):
        FEATURED_PRODUCTS = "FEATURED", "Featured Products"
        BANNER_GRID = "BANNER_GRID", "Banner Grid"
        CATEGORY_CIRCLES = "CATEGORIES", "Category Circles"
        PROMOTIONAL_BANNER = "BANNER", "Promotional Banner"

    title = models.CharField(max_length=255)
    section_type = models.CharField(max_length=20, choices=SectionType.choices)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.get_section_type_display()}: {self.title}"

class Banner(BaseModel):
    section = models.ForeignKey(
        HomepageSection,
        on_delete=models.CASCADE,
        related_name='banners',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='cms/banners/')
    link = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title
