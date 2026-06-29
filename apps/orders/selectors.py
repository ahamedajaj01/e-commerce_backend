from django.db import models
from django.db.models import QuerySet
from .models import Order

class OrderSelector:
    @staticmethod
    def get_user_orders(user) -> QuerySet:
        """Retrieves list of orders for a specific customer."""
        return Order.objects.filter(user=user).prefetch_related('items')

    @staticmethod
    def get_order_for_user(*, user, order_id) -> Order:
        """Retrieves single order detail for ownership verification."""
        return Order.objects.filter(user=user, id=order_id).prefetch_related(
            'items', 'status_history', 'status_history__changed_by'
        ).first()

    @staticmethod
    def get_all_orders() -> QuerySet:
        """Retrieves all orders for administrative use."""
        return Order.objects.all().select_related('user').prefetch_related('items')

    @staticmethod
    def get_order_by_id(order_id) -> Order:
        """Retrieves single order for administrative use."""
        return Order.objects.filter(id=order_id).prefetch_related(
            'items', 'status_history', 'status_history__changed_by'
        ).first()

    @staticmethod
    def get_order_by_number(order_number: str) -> Order:
        """Retrieves public tracking info via order reference number."""
        return Order.objects.filter(order_number=order_number).prefetch_related(
            'status_history'
        ).first()

    @staticmethod
    def filter_orders(queryset: QuerySet, filters: dict) -> QuerySet:
        """Applies administrative filters to a queryset of orders."""
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        if filters.get('payment_status'):
            queryset = queryset.filter(payment_status=filters['payment_status'])
            
        if filters.get('search'):
            search = filters['search']
            queryset = queryset.filter(
                models.Q(order_number__icontains=search) |
                models.Q(customer_name__icontains=search) |
                models.Q(customer_email__icontains=search)
            )
            
        return queryset
