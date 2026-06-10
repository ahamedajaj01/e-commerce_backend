from django.db import models
from core.common.models.base import BaseModel
from apps.catalog.models.product import Category


class NavigationItem(BaseModel):
    menu = models.ForeignKey(
        'cms.NavigationMenu',
        on_delete=models.CASCADE,
        related_name='items'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    title = models.CharField(max_length=255)
    linked_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='navigation_items'
    )
    linked_url = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['sort_order']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # CASCADE: when this nav item is toggled, propagate to the linked content
        if self.linked_category_id:
            Category.objects.filter(pk=self.linked_category_id).update(
                is_active=self.is_active
            )

    def __str__(self):
        return f"{self.menu.title} > {self.title}"

