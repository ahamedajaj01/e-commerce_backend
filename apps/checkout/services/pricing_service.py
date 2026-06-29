from decimal import Decimal
from typing import List
from apps.cart.models.cart import Cart

class PricingService:
    @staticmethod
    def calculate_subtotal(cart: Cart) -> Decimal:
        """Sum of all items in the cart based on their variant prices."""
        return sum(item.variant.price * item.quantity for item in cart.items.all())

    @staticmethod
    def calculate_total(subtotal: Decimal, shipping_fee: Decimal) -> Decimal:
        """Final total price for the session."""
        return subtotal + shipping_fee
