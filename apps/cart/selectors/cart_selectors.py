from typing import Optional
from django.utils import timezone
from ..models.cart import Cart
from ..models.cart_item import CartItem


def get_active_cart(user) -> Optional[Cart]:
    """Retrieve the active cart for an authenticated user."""
    return Cart.objects.filter(
        user=user,
        status=Cart.Status.ACTIVE
    ).first()


def get_active_guest_cart(guest_token: str) -> Optional[Cart]:
    """Retrieve the active cart for a guest by token."""
    if not guest_token:
        return None
    try:
        return Cart.objects.filter(
            guest_token=guest_token,
            user__isnull=True,
            status=Cart.Status.ACTIVE
        ).first()
    except Exception:
        return None


def get_cart_with_items(user) -> Optional[Cart]:
    """Retrieve active authenticated cart with items fetched in a single JOIN."""
    from django.db.models import Prefetch
    
    items_qs = CartItem.objects.select_related('variant__product').prefetch_related('variant__product__media')
    
    return Cart.objects.filter(
        user=user,
        status=Cart.Status.ACTIVE
    ).prefetch_related(
        Prefetch('items', queryset=items_qs)
    ).first()


def get_guest_cart_with_items(guest_token: str) -> Optional[Cart]:
    """Retrieve active guest cart with items fetched in a single JOIN."""
    if not guest_token:
        return None
        
    from django.db.models import Prefetch
    items_qs = CartItem.objects.select_related('variant__product').prefetch_related('variant__product__media')

    return Cart.objects.filter(
        guest_token=guest_token,
        user__isnull=True,
        status=Cart.Status.ACTIVE
    ).prefetch_related(
        Prefetch('items', queryset=items_qs)
    ).first()


def get_cart_item(cart: Cart, variant_id: str) -> Optional[CartItem]:
    """Retrieve a specific item from a cart."""
    return CartItem.objects.filter(cart=cart, variant_id=variant_id).first()
