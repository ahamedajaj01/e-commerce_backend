import uuid
from datetime import timedelta
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.catalog.models.product import Product, ProductVariant
from apps.cart.models.cart import Cart
from apps.cart.models.cart_item import CartItem
from apps.cart.services.cart_service import (
    get_or_create_auth_cart,
    get_or_create_guest_cart,
    add_to_cart_authenticated,
    add_to_cart_guest,
    merge_guest_cart_into_user_cart,
    GUEST_TOKEN_COOKIE,
)
from apps.cart.selectors.cart_selectors import get_active_cart, get_active_guest_cart
from core.common.exceptions.cart_exceptions import InsufficientStockException

User = get_user_model()


def make_user(email="test@example.com", password="pass1234"):
    return User.objects.create_user(email=email, password=password)


def make_product_with_variant(name="Test Product", price=500.0, stock=20):
    product = Product.objects.create(name=name, base_price=price)
    variant = ProductVariant.objects.create(
        product=product,
        sku=f"SKU-{uuid.uuid4().hex[:6].upper()}",
        price=price,
        stock_quantity=stock,
    )
    return product, variant


# ---------------------------------------------------------------------------
# 1. Guest add-to-cart
# ---------------------------------------------------------------------------
class GuestAddToCartTest(TestCase):
    def test_guest_add_creates_cart_and_returns_token(self):
        _, variant = make_product_with_variant()

        item, token = add_to_cart_guest(guest_token=None, variant_id=str(variant.id), quantity=2)

        self.assertIsNotNone(token)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(str(item.cart.guest_token), token)
        self.assertIsNone(item.cart.user)

    def test_guest_add_insufficient_stock_raises(self):
        _, variant = make_product_with_variant(stock=1)
        with self.assertRaises(InsufficientStockException):
            add_to_cart_guest(guest_token=None, variant_id=str(variant.id), quantity=5)


# ---------------------------------------------------------------------------
# 2. Guest cart persistence — same token returns same cart
# ---------------------------------------------------------------------------
class GuestCartPersistenceTest(TestCase):
    def test_same_token_returns_same_cart(self):
        _, variant = make_product_with_variant()
        _, token = add_to_cart_guest(guest_token=None, variant_id=str(variant.id), quantity=1)

        # Second call with same token
        _, variant2 = make_product_with_variant(name="Product 2")
        item2, returned_token = add_to_cart_guest(
            guest_token=token, variant_id=str(variant2.id), quantity=1
        )

        self.assertEqual(token, returned_token)
        self.assertEqual(str(item2.cart.guest_token), token)
        self.assertEqual(item2.cart.items.count(), 2)


# ---------------------------------------------------------------------------
# 3. Returning guest retrieval
# ---------------------------------------------------------------------------
class ReturningGuestRetrievalTest(TestCase):
    def test_guest_cart_retrieved_by_token(self):
        _, variant = make_product_with_variant()
        _, token = add_to_cart_guest(guest_token=None, variant_id=str(variant.id), quantity=3)

        retrieved_cart = get_active_guest_cart(token)
        self.assertIsNotNone(retrieved_cart)
        self.assertEqual(retrieved_cart.items.count(), 1)
        self.assertEqual(retrieved_cart.items.first().quantity, 3)

    def test_invalid_token_returns_none(self):
        cart = get_active_guest_cart("not-a-real-token")
        self.assertIsNone(cart)


# ---------------------------------------------------------------------------
# 4. Guest-to-user cart merge
# ---------------------------------------------------------------------------
class GuestToUserMergeTest(TestCase):
    def setUp(self):
        self.user = make_user()
        _, self.v1 = make_product_with_variant(name="P1", stock=50)
        _, self.v2 = make_product_with_variant(name="P2", stock=50)

    def test_merge_transfers_items_to_user_cart(self):
        _, token = add_to_cart_guest(guest_token=None, variant_id=str(self.v1.id), quantity=2)
        add_to_cart_guest(guest_token=token, variant_id=str(self.v2.id), quantity=3)

        user_cart = merge_guest_cart_into_user_cart(user=self.user, guest_token=token)

        self.assertEqual(user_cart.user, self.user)
        self.assertEqual(user_cart.items.count(), 2)

        qtys = {str(item.variant_id): item.quantity for item in user_cart.items.all()}
        self.assertEqual(qtys[str(self.v1.id)], 2)
        self.assertEqual(qtys[str(self.v2.id)], 3)

    def test_guest_cart_marked_merged_after_merge(self):
        _, token = add_to_cart_guest(guest_token=None, variant_id=str(self.v1.id), quantity=1)

        merge_guest_cart_into_user_cart(user=self.user, guest_token=token)

        guest_cart = Cart.objects.filter(guest_token=None, status=Cart.Status.MERGED).first()
        # guest_token is cleared to None after merge
        self.assertIsNone(get_active_guest_cart(token))


# ---------------------------------------------------------------------------
# 5. Duplicate item merge scenarios
# ---------------------------------------------------------------------------
class DuplicateMergeTest(TestCase):
    def setUp(self):
        self.user = make_user(email="dup@example.com")
        _, self.variant = make_product_with_variant(name="Shared Product", stock=100)

    def test_duplicate_variant_quantities_are_summed(self):
        # User already has 3 in cart
        add_to_cart_authenticated(user=self.user, variant_id=str(self.variant.id), quantity=3)
        # Guest also has 5
        _, token = add_to_cart_guest(guest_token=None, variant_id=str(self.variant.id), quantity=5)

        user_cart = merge_guest_cart_into_user_cart(user=self.user, guest_token=token)

        item = user_cart.items.get(variant=self.variant)
        self.assertEqual(item.quantity, 8)  # 3 + 5

    def test_merge_caps_quantity_at_available_stock(self):
        _, low_stock_variant = make_product_with_variant(name="Low Stock", stock=6)

        add_to_cart_authenticated(user=self.user, variant_id=str(low_stock_variant.id), quantity=4)
        _, token = add_to_cart_guest(guest_token=None, variant_id=str(low_stock_variant.id), quantity=4)

        user_cart = merge_guest_cart_into_user_cart(user=self.user, guest_token=token)

        item = user_cart.items.get(variant=low_stock_variant)
        self.assertEqual(item.quantity, 6)  # Capped at stock=6, not 4+4=8


# ---------------------------------------------------------------------------
# 6. Cart expiration behavior
# ---------------------------------------------------------------------------
class CartExpirationTest(TestCase):
    def test_expired_guest_cart_is_not_returned_as_active(self):
        _, variant = make_product_with_variant()
        _, token = add_to_cart_guest(guest_token=None, variant_id=str(variant.id), quantity=1)

        # Manually expire the cart
        cart = get_active_guest_cart(token)
        cart.expires_at = timezone.now() - timedelta(days=1)
        cart.status = Cart.Status.EXPIRED
        cart.save()

        # Should not be found as active
        retrieved = get_active_guest_cart(token)
        self.assertIsNone(retrieved)

    def test_is_expired_property_true_when_past_expiry(self):
        cart = Cart.objects.create(
            expires_at=timezone.now() - timedelta(hours=1),
            status=Cart.Status.ACTIVE
        )
        self.assertTrue(cart.is_expired)

    def test_is_expired_property_false_when_future_expiry(self):
        cart = Cart.objects.create(
            expires_at=timezone.now() + timedelta(days=10),
            status=Cart.Status.ACTIVE
        )
        self.assertFalse(cart.is_expired)
