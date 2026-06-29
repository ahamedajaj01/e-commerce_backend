import uuid
from django.db import models
from django.conf import settings
from core.common.models.base import BaseModel
from apps.shipping.models.shipping import ShippingRule


class CheckoutSession(BaseModel):
    """
    Orchestration model that stores the temporary state of a checkout process.
    Acts as a bridge between Cart and Order.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PAYMENT_PENDING = 'PAYMENT_PENDING', 'Payment Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class PaymentMethod(models.TextChoices):
        COD = 'COD', 'Cash on Delivery'
        BANK = 'BANK', 'Bank Transfer'
        ESEWA = 'ESEWA', 'eSewa'
        KHALTI = 'KHALTI', 'Khalti'
        ONLINE = 'ONLINE', 'Online Payment'

    # Identity & Linkage
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='checkout_sessions'
    )
    guest_token = models.UUIDField(null=True, blank=True, help_text="For guest checkouts")
    cart = models.ForeignKey(
        'cart.Cart', 
        on_delete=models.CASCADE, 
        related_name='checkout_sessions'
    )

    # Status & Life-cycle
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    expires_at = models.DateTimeField()

    # Customer Snapshot (from checkout form)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    # Address Snapshot
    shipping_province = models.CharField(max_length=100)
    shipping_district = models.CharField(max_length=100)
    shipping_city = models.CharField(max_length=100)
    shipping_street = models.CharField(max_length=255)
    shipping_instructions = models.TextField(blank=True, default='')

    # Shipping Domain Snapshot
    shipping_rule = models.ForeignKey(
        ShippingRule, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='sessions'
    )
    shipping_rule_title = models.CharField(max_length=255) # Snapshot for audit
    
    # Delivery ETA Snapshot
    transit_days_min = models.PositiveIntegerField(default=0)
    transit_days_max = models.PositiveIntegerField(default=0)
    processing_days_max = models.PositiveIntegerField(default=0)
    
    # Financial Snapshot
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Payment Integration
    payment_method = models.CharField(max_length=100, blank=True, default='')
    payment_id = models.CharField(max_length=255, blank=True, default='', help_text="External gateway transaction ID")
    payment_metadata = models.JSONField(default=dict, blank=True)

    # Resulting Order
    order = models.OneToOneField(
        'orders.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='checkout_session'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Checkout {self.id} ({self.status})"
