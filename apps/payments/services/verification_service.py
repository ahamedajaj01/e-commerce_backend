from django.utils import timezone
from django.db import transaction
from ..models import PaymentTransaction
from apps.orders.models import Order

class VerificationService:
    @staticmethod
    @transaction.atomic
    def verify_transaction(
        *,
        transaction_obj: PaymentTransaction,
        admin_user,
        approve: bool,
        notes: str = ""
    ) -> PaymentTransaction:
        """
        Finalizes a manual payment review.
        If approved, it syncs the status back to the Order.
        """
        if approve:
            transaction_obj.status = PaymentTransaction.Status.APPROVED
            # Sync with the order domain
            order = transaction_obj.order
            order.is_paid = True
            order.payment_status = Order.PaymentStatus.PAID
            # Update the payment method snapshot on the order to the actual method used
            order.payment_method = transaction_obj.payment_method.name
            order.save()
        else:
            transaction_obj.status = PaymentTransaction.Status.REJECTED
            # Sync rejection back to the order
            order = transaction_obj.order
            order.payment_status = Order.PaymentStatus.FAILED
            order.save()

        transaction_obj.verified_at = timezone.now()
        transaction_obj.verified_by = admin_user
        transaction_obj.admin_notes = notes
        transaction_obj.save()
        
        return transaction_obj
