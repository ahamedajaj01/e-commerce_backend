import uuid
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.catalog.models.product import ProductVariant
from ..models.cart import Cart
from ..models.cart_item import CartItem
from ..selectors.cart_selectors import (
    get_active_cart,
    get_active_guest_cart,
    get_cart_item,
)
from core.common.exceptions.cart_exceptions import (
    InsufficientStockException,
    VariantNotAvailableException
)

User = get_user_model()

GUEST_CART_TTL_DAYS = 30
GUEST_TOKEN_COOKIE = "guest_cart_token"


# ---------------------------------------------------------------------------
# Cart Retrieval / Creation
# ---------------------------------------------------------------------------

def get_or_create_auth_cart(user: User) -> Cart:
    """Get or create an active cart for an authenticated user."""
    cart = get_active_cart(user)
    if not cart:
        cart = Cart.objects.create(user=user, status=Cart.Status.ACTIVE)
    return cart


def get_or_create_guest_cart(guest_token: str = None) -> tuple[Cart, str]:
    """
    Get or create a guest cart.
    Returns (cart, guest_token) — the token may be newly generated.
    """
    if guest_token:
        cart = get_active_guest_cart(guest_token)
        if cart:
            # Refresh expiry on access
            cart.expires_at = timezone.now() + timedelta(days=GUEST_CART_TTL_DAYS)
            cart.save(update_fields=['expires_at'])
            return cart, guest_token

    # Generate a new guest token and cart
    new_token = str(uuid.uuid4())
    cart = Cart.objects.create(
        user=None,
        guest_token=new_token,
        status=Cart.Status.ACTIVE,
        expires_at=timezone.now() + timedelta(days=GUEST_CART_TTL_DAYS),
    )
    return cart, new_token


# ---------------------------------------------------------------------------
# Add to Cart
# ---------------------------------------------------------------------------

@transaction.atomic
def add_to_cart_authenticated(*, user: User, variant_id: str, quantity: int = 1) -> CartItem:
    cart = get_or_create_auth_cart(user)
    return _add_item_to_cart(cart=cart, variant_id=variant_id, quantity=quantity)


@transaction.atomic
def add_to_cart_guest(*, guest_token: str = None, variant_id: str, quantity: int = 1) -> tuple[CartItem, str]:
    cart, token = get_or_create_guest_cart(guest_token)
    item = _add_item_to_cart(cart=cart, variant_id=variant_id, quantity=quantity)
    return item, token


def _add_item_to_cart(*, cart: Cart, variant_id: str, quantity: int) -> CartItem:
    """Optimized internal logic to save round-trips to Supabase."""
    # 1. Combined lookup: Check variant existence and stock in one trip
    # We also select_related the product to help with serialization later
    try:
        variant = ProductVariant.objects.select_related('product').get(id=variant_id, is_active=True)
    except ProductVariant.DoesNotExist:
        raise VariantNotAvailableException()

    if variant.stock_quantity < quantity:
        raise InsufficientStockException()

    # 2. Optimized Check + Update
    # Using select_related('variant') here ensures serialization of the return value is fast
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        variant=variant,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if variant.stock_quantity < new_quantity:
            raise InsufficientStockException()
        cart_item.quantity = new_quantity
        cart_item.save(update_fields=['quantity'])

    return cart_item


# ---------------------------------------------------------------------------
# Update / Remove
# ---------------------------------------------------------------------------

@transaction.atomic
def update_cart_item_quantity(*, cart_item: CartItem, quantity: int) -> CartItem:
    if quantity < 1:
        cart_item.delete()
        return None

    # Ensure variant is prefetched or fetched to avoid an extra trip for stock check
    # If the view doesn't pass a prefetched item, this will trigger one trip.
    if cart_item.variant.stock_quantity < quantity:
        raise InsufficientStockException()

    cart_item.quantity = quantity
    cart_item.save(update_fields=['quantity'])
    return cart_item


@transaction.atomic
def remove_from_cart(*, cart_item: CartItem) -> None:
    cart_item.delete()


@transaction.atomic
def clear_cart(*, cart: Cart) -> None:
    cart.items.all().delete()


# ---------------------------------------------------------------------------
# Merge Flow (called on login)
# ---------------------------------------------------------------------------

@transaction.atomic
def merge_guest_cart_into_user_cart(*, user: User, guest_token: str) -> Cart:
    """
    Merge a guest cart into the authenticated user's cart on login.
    - Finds guest cart by token.
    - Finds or creates the user's active cart.
    - Merges all guest items (increasing quantity if the variant already exists).
    - Marks the guest cart as MERGED.
    Returns the merged user cart.
    """
    guest_cart = get_active_guest_cart(guest_token)
    if not guest_cart:
        # No guest cart to merge — just return the user cart
        return get_or_create_auth_cart(user)

    user_cart = get_or_create_auth_cart(user)

    for guest_item in guest_cart.items.select_related('variant').all():
        variant = guest_item.variant

        # Skip if variant is no longer active
        if not variant.is_active:
            continue

        existing = get_cart_item(user_cart, str(variant.id))
        if existing:
            # Merge: increase quantity but cap at available stock
            merged_qty = existing.quantity + guest_item.quantity
            if variant.stock_quantity < merged_qty:
                merged_qty = variant.stock_quantity  # Cap to max available
            existing.quantity = merged_qty
            existing.save()
        else:
            # Transfer the item to the user cart
            # Cap quantity to available stock defensively
            transfer_qty = min(guest_item.quantity, variant.stock_quantity)
            if transfer_qty > 0:
                CartItem.objects.create(
                    cart=user_cart,
                    variant=variant,
                    quantity=transfer_qty
                )

    # Mark the guest cart as MERGED and detach the token
    guest_cart.status = Cart.Status.MERGED
    guest_cart.guest_token = None
    guest_cart.save(update_fields=['status', 'guest_token'])

    return user_cart


# ---------------------------------------------------------------------------
# Legacy compatibility — keeps existing auth-only view calls working
# ---------------------------------------------------------------------------

def add_to_cart(*, user: User, variant_id: str, quantity: int = 1) -> CartItem:
    """Backward-compat wrapper for authenticated add to cart."""
    return add_to_cart_authenticated(user=user, variant_id=variant_id, quantity=quantity)


def get_or_create_cart(user: User) -> Cart:
    """Backward-compat wrapper."""
    return get_or_create_auth_cart(user)
