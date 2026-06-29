from django.db.models import QuerySet
from .models import PaymentMethod, PaymentTransaction, PaymentProvider

class PaymentSelector:
    @staticmethod
    def get_active_methods() -> QuerySet:
        """Returns active payment methods for the buyer to choose from."""
        return PaymentMethod.objects.filter(is_active=True).select_related('provider').order_by('display_order')

    @staticmethod
    def get_transaction_by_id(transaction_id) -> PaymentTransaction:
        """Retrieves a single transaction with proofs for the admin."""
        return PaymentTransaction.objects.prefetch_related('proofs').get(id=transaction_id)

    @staticmethod
    def get_all_transactions() -> QuerySet:
        """Retrieves all payment attempts for administrative auditing."""
        return PaymentTransaction.objects.all().select_related('order', 'payment_method')

    @staticmethod
    def filter_transactions(queryset: QuerySet, filters: dict) -> QuerySet:
        """Applies filters (status, method, etc.) to the transaction list."""
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        if filters.get('order_number'):
            queryset = queryset.filter(order__order_number__icontains=filters['order_number'])
            
        return queryset
