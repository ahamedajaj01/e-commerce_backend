from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.common.responses.formatters import success_response, error_response
from ...selectors import OrderSelector
from ..serializers import OrderListSerializer, OrderDetailSerializer, OrderTrackingSerializer

class OrderListView(APIView):
    """
    GET /api/v1/storefront/orders/
    Returns list of orders for the authenticated customer.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders_qs = OrderSelector.get_user_orders(request.user)
        
        # Simple pagination if needed
        from core.utils.pagination import paginate_queryset
        paginated_qs, meta = paginate_queryset(orders_qs, page=int(request.query_params.get('page', 1)))
        
        serializer = OrderListSerializer(paginated_qs, many=True)
        return success_response(data={"results": serializer.data, "meta": meta})


class OrderDetailView(APIView):
    """
    GET /api/v1/storefront/orders/{id}/
    Returns full detail of a specific order owned by the user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = OrderSelector.get_order_for_user(user=request.user, order_id=order_id)
        if not order:
            return error_response(message="Order not found", status_code=404)
        
        serializer = OrderDetailSerializer(order)
        return success_response(data=serializer.data)


class OrderTrackingView(APIView):
    """
    GET /api/v1/storefront/orders/track/
    Public unauthenticated tracking using order number.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        order_number = request.query_params.get('number')
        if not order_number:
            return error_response(message="Order number is required", status_code=400)

        # Always use the selector for domain logic
        order = OrderSelector.get_order_by_number(order_number)
        
        if not order:
            return error_response(message="No order found with this tracking number", status_code=404)

        # Uses the anonymized tracking serializer
        serializer = OrderTrackingSerializer(order)
        return success_response(data=serializer.data)
