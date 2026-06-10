import uuid
from django.db import models
from core.common.models.base import BaseModel


class ShippingProvider(BaseModel):
    """
    Represents a shipping service provider (e.g., Manual, Pathao, Aramex).
    Kept for future courier API integrations.
    """
    class ProviderType(models.TextChoices):
        MANUAL = 'MANUAL', 'Manual/Internal'
        API = 'API', 'External API'

    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True)
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices, default=ProviderType.MANUAL)
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)  # Stores API keys for future providers

    def __str__(self):
        return self.name


class ShippingRule(BaseModel):
    """
    A flat, hierarchical shipping rule.

    Supports four levels of geographic specificity:
        Priority 1 (Most Specific): Province + District + City/Municipality
        Priority 2: Province + District
        Priority 3: Province Only
        Priority 4 (Default): is_default=True, no geo-filtering

    Matching stops at first valid rule. If no rule matches, shipping is unavailable.
    Admin should NOT need neighborhood-level (Anamnagar, Baneshwor) entries.
    City/District-level coverage is sufficient; Google Places will normalize user input.
    """
    title = models.CharField(max_length=150, help_text="Human-readable label e.g. 'Kathmandu District'")

    # Geographic Scope (all optional for flexibility)
    province = models.CharField(max_length=100, blank=True, default='')
    district = models.CharField(max_length=100, blank=True, default='')
    city_or_municipality = models.CharField(max_length=100, blank=True, default='')

    # Pricing
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.CharField(max_length=50, blank=True, default='3-5 Business Days')

    # Rule Metadata
    priority = models.PositiveIntegerField(
        default=10,
        help_text="Lower number = higher priority. Auto-set based on geo-specificity."
    )
    is_default = models.BooleanField(
        default=False,
        help_text="If True, this rule applies to any address with no other match. Only one default allowed."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['priority', 'province', 'district', 'city_or_municipality']

    def save(self, *args, **kwargs):
        # Auto-calculate priority based on geo-specificity
        if self.is_default:
            self.priority = 100  # Lowest priority
        elif self.city_or_municipality:
            self.priority = 10  # Most specific
        elif self.district:
            self.priority = 20
        elif self.province:
            self.priority = 30
        else:
            self.priority = 100  # Effectively default
        super().save(*args, **kwargs)

    def __str__(self):
        parts = [p for p in [self.province, self.district, self.city_or_municipality] if p]
        scope = " / ".join(parts) if parts else "Default (Nationwide)"
        return f"{self.title} [{scope}] - NPR {self.shipping_fee}"
