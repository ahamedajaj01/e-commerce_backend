import uuid
from django.db import models
from django.conf import settings
from core.common.models.base import BaseModel


class Order(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        AWAITING_VERIFICATION = 'AWAITING_VERIFICATION', 'Awaiting Verification'
        PAID = 'PAID', 'Payment Verified'
        FAILED = 'FAILED', 'Failed / Rejected'
        REFUNDED = 'REFUNDED', 'Refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders'
    )
    
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        db_index=True
    )
    
    # 📸 Customer Snapshot
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # 📸 Shipping Address Snapshot
    shipping_province = models.CharField(max_length=100)
    shipping_district = models.CharField(max_length=100)
    shipping_city = models.CharField(max_length=100)
    shipping_street = models.CharField(max_length=255)
    shipping_instructions = models.TextField(blank=True)
    
    # 🚚 ETA Snapshot
    transit_days_min = models.PositiveIntegerField(default=0)
    transit_days_max = models.PositiveIntegerField(default=0)
    processing_days_max = models.PositiveIntegerField(default=0)
    
    # 💰 Financials
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # 💳 Payment Tracking
    payment_method = models.CharField(max_length=100)
    payment_status = models.CharField(
        max_length=30, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.UNPAID
    )
    is_paid = models.BooleanField(default=False)
    transaction_reference = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(
        'catalog.ProductVariant', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='order_items'
    )
    
    # 📸 Product Snapshot
    product_id = models.UUIDField(null=True)
    variant_id = models.UUIDField(null=True)
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    variant_image = models.URLField(max_length=500, blank=True, default='')
    
    # 💰 Price Snapshot
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name} ({self.sku})"


class OrderStatusHistory(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=20, choices=Order.Status.choices, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=Order.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = "Order status histories"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number}: {self.previous_status} -> {self.new_status}"
