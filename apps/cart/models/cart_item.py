from django.db import models
from core.common.models.base import BaseModel
from .cart import Cart
from apps.catalog.models.product import ProductVariant

class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'variant')

    @property
    def subtotal(self):
        return self.variant.price * self.quantity

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"
