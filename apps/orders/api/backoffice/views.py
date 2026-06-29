from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsBackofficeStaff
from core.common.responses.formatters import success_response, error_response
from ...selectors import OrderSelector
from ...services.status_service import OrderStatusService
from ..serializers import OrderListSerializer, OrderDetailSerializer, OrderStatusUpdateSerializer

class AdminOrderListView(APIView):
    """
    GET /api/v1/backoffice/orders/
    Administrative view for listing and filtering all orders.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        orders_qs = OrderSelector.get_all_orders()
        
        # Apply Admin filters
        filters = {
            'status': request.query_params.get('status'),
            'payment_status': request.query_params.get('payment_status'),
            'search': request.query_params.get('search'),
        }
        orders_qs = OrderSelector.filter_orders(orders_qs, filters)
        
        from core.utils.pagination import paginate_queryset
        paginated_qs, meta = paginate_queryset(orders_qs, page=int(request.query_params.get('page', 1)))
        
        serializer = OrderListSerializer(paginated_qs, many=True, context={'request': request})
        return success_response(data={"results": serializer.data, "meta": meta})


class AdminOrderDetailView(APIView):
    """
    GET /api/v1/backoffice/orders/{id}/
    Administrative view for order details and auditing.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request, order_id):
        order = OrderSelector.get_order_by_id(order_id)
        if not order:
            return error_response(message="Order not found", status_code=404)
        
        serializer = OrderDetailSerializer(order, context={'request': request})
        return success_response(data=serializer.data)

    def patch(self, request, order_id):
        """
        PATCH /api/v1/backoffice/orders/{id}/
        Update order status or payment status with notes.
        """
        order = OrderSelector.get_order_by_id(order_id)
        if not order:
            return error_response(message="Order not found", status_code=404)
        
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid data", data=serializer.errors)
        
        data = serializer.validated_data
        
        # 1. Update Order Status (if provided)
        if 'status' in data:
            order = OrderStatusService.update_status(
                order=order,
                new_status=data['status'],
                user=request.user,
                notes=data.get('notes', '')
            )
        
        # 2. Update Payment Status (if provided)
        if 'payment_status' in data:
            order.payment_status = data['payment_status']
            if data['payment_status'] == order.PaymentStatus.PAID:
                order.is_paid = True
            elif data['payment_status'] in [order.PaymentStatus.FAILED, order.PaymentStatus.UNPAID]:
                order.is_paid = False
            order.save()
            
            # Log payment status change if no status change was done (to ensure notes are saved)
            if 'status' not in data and data.get('notes'):
                from ...models import OrderStatusHistory
                OrderStatusHistory.objects.create(
                    order=order,
                    previous_status=order.status,
                    new_status=order.status,
                    changed_by=request.user,
                    notes=f"[Payment Status Update to {data['payment_status']}] {data.get('notes')}"
                )
        
        return success_response(
            data=OrderDetailSerializer(order, context={'request': request}).data,
            message="Order updated successfully"
        )
