from rest_framework.views import APIView
from rest_framework import status
from core.common.responses.formatters import success_response, error_response
from .serializers import CheckoutSessionCreateSerializer, CheckoutSessionSerializer
from ...services.session_service import CheckoutSessionService
from ...models.session import CheckoutSession

from apps.cart.selectors.cart_selectors import get_cart_with_items, get_guest_cart_with_items
from apps.cart.api.storefront.views import _get_guest_token
from apps.shipping.models.shipping import ShippingRule


class CheckoutSessionCreateView(APIView):
    """
    POST /api/v1/storefront/checkout/sessions/
    Initializes a checkout session from the form data.
    """
    permission_classes = []

    def post(self, request):
        serializer = CheckoutSessionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid data", data=serializer.errors)

        data = serializer.validated_data
        
        # 1. Identify Cart
        if request.user.is_authenticated:
            cart = get_cart_with_items(request.user)
        else:
            guest_token = _get_guest_token(request)
            cart = get_guest_cart_with_items(guest_token)

        if not cart or cart.items.count() == 0:
            return error_response(message="Your cart is empty", status_code=400)

        # 2. Get Shipping Rule
        try:
            shipping_rule = ShippingRule.objects.get(id=data['shipping_rule_id'], is_active=True)
        except ShippingRule.DoesNotExist:
            return error_response(message="Invalid shipping rule", status_code=400)

        # 3. Initialize Session
        session = CheckoutSessionService.init_session(
            cart=cart,
            customer_data={
                'name': data['name'],
                'email': data['email'],
                'phone': data['phone']
            },
            shipping_address={
                'province': data['province'],
                'district': data['district'],
                'city': data['city'],
                'street': data['street'],
                'instructions': data.get('instructions', '')
            },
            shipping_rule=shipping_rule,
            payment_method="", 
            user=request.user if request.user.is_authenticated else None,
            guest_token=None if request.user.is_authenticated else _get_guest_token(request)
        )

        return success_response(
            data=CheckoutSessionSerializer(session).data,
            status_code=status.HTTP_201_CREATED
        )


class CheckoutSessionDetailView(APIView):
    """
    GET /api/v1/storefront/checkout/sessions/{id}/
    PATCH /api/v1/storefront/checkout/sessions/{id}/
    Retrieves or updates a session (used for the Payment summary page).
    """
    permission_classes = []
    
    def get(self, request, session_id):
        try:
            session = CheckoutSession.objects.get(id=session_id)
            return success_response(data=CheckoutSessionSerializer(session).data)
        except CheckoutSession.DoesNotExist:
            return error_response(message="Session not found", status_code=404)

    def patch(self, request, session_id):
        try:
            session = CheckoutSession.objects.get(id=session_id)
            payment_method = request.data.get('payment_method')
            if payment_method:
                # Basic validation against model choices if needed
                session.payment_method = payment_method
                session.save()
            return success_response(data=CheckoutSessionSerializer(session).data)
        except CheckoutSession.DoesNotExist:
            return error_response(message="Session not found", status_code=404)


class CheckoutSessionCompleteView(APIView):
    """
    POST /api/v1/storefront/checkout/sessions/{id}/complete/
    Finalizes the checkout and creates the order.
    """
    permission_classes = []

    def post(self, request, session_id):
        try:
            session = CheckoutSession.objects.get(id=session_id)
        except CheckoutSession.DoesNotExist:
            return error_response(message="Session not found", status_code=404)

        if session.status == CheckoutSession.Status.COMPLETED:
             return success_response(message="Order already created", data={"order_id": session.order_id})

        # Logic for Online Payment would check for success here
        # For COD, we can complete immediately
        
        try:
            order = CheckoutSessionService.complete_session(session)
        except ValueError as e:
            return error_response(message=str(e), status_code=400)
        
        return success_response(
            data={"order_number": order.order_number, "order_id": order.id},
            message="Your order has been placed successfully!"
        )
