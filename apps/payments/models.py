import uuid
from django.db import models
from django.conf import settings
from core.common.models.base import BaseModel


class PaymentProvider(BaseModel):
    """
    Represents the underlying technical implementation (e.g., Manual, Khalti, eSewa).
    """
    class ProviderType(models.TextChoices):
        MANUAL = 'MANUAL', 'Manual'
        GATEWAY = 'GATEWAY', 'API Gateway'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices, default=ProviderType.MANUAL)
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True, help_text="API keys or account details")

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"


class PaymentMethod(BaseModel):
    """
    The customer-facing payment choice (e.g., Bank Transfer, COD).
    """
    class PaymentType(models.TextChoices):
        COD = 'COD', 'Cash on Delivery'
        BANK = 'BANK', 'Bank Transfer'
        ESEWA = 'ESEWA', 'eSewa'
        KHALTI = 'KHALTI', 'Khalti'
        MANUAL = 'MANUAL', 'Manual Payment'
        GATEWAY = 'GATEWAY', 'Gateway Payment'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(PaymentProvider, on_delete=models.PROTECT, related_name='methods')
    
    # Display Properties
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, help_text="Step-by-step payment guide")
    qr_image = models.ImageField(upload_to='payments/qr_codes/', null=True, blank=True)
    
    # Logic / Workflow
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    requires_proof = models.BooleanField(default=False, help_text="Customer must upload screenshot")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class PaymentTransaction(BaseModel):
    """
    The source of truth for a payment attempt on an order.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='transactions')
    
    # Financials
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='NPR')
    
    # Status / Verification
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_reference = models.CharField(max_length=255, blank=True, default='', help_text="Gateway reference or customer UTR")
    
    # Auditing
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_payments'
    )
    admin_notes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Payment for {self.order.order_number} - {self.status}"


class PaymentProof(BaseModel):
    """
    Customer-uploaded screenshots or digital receipts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='proofs')
    image = models.ImageField(upload_to='payments/proofs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for {self.transaction.id}"
