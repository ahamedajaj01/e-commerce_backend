from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from core.common.responses.formatters import success_response, error_response
from ...selectors.cart_selectors import get_cart_with_items, get_guest_cart_with_items
from ...services.cart_service import (
    add_to_cart_authenticated,
    add_to_cart_guest,
    update_cart_item_quantity,
    remove_from_cart,
    get_or_create_auth_cart,
    get_or_create_guest_cart,
    GUEST_TOKEN_COOKIE,
)
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer, CartItemSerializer
from ...models.cart_item import CartItem


def _get_guest_token(request) -> str:
    """Read the guest cart token from the request cookie."""
    return request.COOKIES.get(GUEST_TOKEN_COOKIE)


def _set_guest_cookie(response, token: str):
    """Write the guest cart token to a secure, SameSite cookie."""
    is_secure = not settings.DEBUG
    response.set_cookie(
        GUEST_TOKEN_COOKIE,
        str(token),
        max_age=60 * 60 * 24 * 30,  # 30 days in seconds
        httponly=True,
        samesite='Lax',
        secure=is_secure,
    )


class CartDetailView(APIView):
    permission_classes = []  # Allow both anonymous and authenticated

    def get(self, request):
        if request.user.is_authenticated:
            cart = get_cart_with_items(request.user)
            if not cart:
                cart = get_or_create_auth_cart(request.user)
        else:
            guest_token = _get_guest_token(request)
            cart = get_guest_cart_with_items(guest_token)
            if not cart:
                # Return an empty cart placeholder without persisting it
                return success_response(data={
                    "id": None,
                    "items": [],
                    "total_quantity": 0,
                    "total_price": "0.00",
                    "status": "ACTIVE",
                    "is_guest": True,
                })

        serializer = CartSerializer(cart)
        return success_response(data=serializer.data)


class CartItemAddView(APIView):
    permission_classes = []  # Allow both anonymous and authenticated

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid data", data=serializer.errors)

        variant_id = serializer.validated_data['variant_id']
        quantity = serializer.validated_data['quantity']

        if request.user.is_authenticated:
            cart_item = add_to_cart_authenticated(
                user=request.user,
                variant_id=str(variant_id),
                quantity=quantity
            )
            response = success_response(
                data=CartItemSerializer(cart_item).data,
                message="Item added to cart",
                status_code=status.HTTP_201_CREATED
            )
        else:
            guest_token = _get_guest_token(request)
            cart_item, new_token = add_to_cart_guest(
                guest_token=guest_token,
                variant_id=str(variant_id),
                quantity=quantity
            )
            response = success_response(
                data=CartItemSerializer(cart_item).data,
                message="Item added to cart",
                status_code=status.HTTP_201_CREATED
            )
            # Always set the cookie back in case a new token was generated
            if new_token != guest_token:
                _set_guest_cookie(response, new_token)

        return response


class CartItemDetailView(APIView):
    permission_classes = []

    def _get_cart_item(self, request, item_id) -> CartItem:
        """Retrieve a CartItem that belongs to the current session (auth or guest)."""
        if request.user.is_authenticated:
            return CartItem.objects.filter(
                id=item_id,
                cart__user=request.user,
                cart__status='ACTIVE'
            ).select_related('variant').first()
        else:
            guest_token = _get_guest_token(request)
            if not guest_token:
                return None
            return CartItem.objects.filter(
                id=item_id,
                cart__guest_token=guest_token,
                cart__status='ACTIVE'
            ).select_related('variant').first()

    def patch(self, request, item_id):
        cart_item = self._get_cart_item(request, item_id)
        if not cart_item:
            return error_response(message="Cart item not found", status_code=404)

        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid data", data=serializer.errors)

        updated_item = update_cart_item_quantity(
            cart_item=cart_item,
            quantity=serializer.validated_data['quantity']
        )

        if updated_item:
            return success_response(data=CartItemSerializer(updated_item).data, message="Cart updated")
        return success_response(message="Item removed from cart")

    def delete(self, request, item_id):
        cart_item = self._get_cart_item(request, item_id)
        if not cart_item:
            return error_response(message="Cart item not found", status_code=404)

        remove_from_cart(cart_item=cart_item)
        return success_response(message="Item removed from cart")
