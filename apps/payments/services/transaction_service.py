from django.db import transaction

from apps.orders.models import Order
from ..models import PaymentTransaction, PaymentProof, PaymentMethod


class TransactionService:
    @staticmethod
    @transaction.atomic
    def init_transaction(*, order, payment_method: PaymentMethod) -> PaymentTransaction:
        """
        Starts a new payment attempt for an order.
        Moves status to SUBMITTED immediately if it's COD.
        """
        status = PaymentTransaction.Status.PENDING
        
        # If COD, it doesn't need proof and starts as pending/ready
        if payment_method.payment_type == PaymentMethod.PaymentType.COD:
            status = PaymentTransaction.Status.PENDING # Awaiting delivery

        transaction_obj = PaymentTransaction.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_price,
            status=status
        )

        # Sync the order's payment details
        order.payment_method = payment_method.name
        order.transaction_reference = str(transaction_obj.id)
        order.payment_status = Order.PaymentStatus.AWAITING_VERIFICATION
        order.save()

        # Also sync the CheckoutSession if it exists
        try:
            session = order.checkout_session
            session.payment_method = payment_method.name
            session.payment_id = str(transaction_obj.id)
            session.payment_metadata = {
                "transaction_uuid": str(transaction_obj.id),
                "provider_type": payment_method.provider.provider_type,
                "requires_proof": payment_method.requires_proof
            }
            session.save()
        except:
            pass

        return transaction_obj

    @staticmethod
    def submit_proof(*, transaction_obj: PaymentTransaction, proof_image) -> PaymentProof:
        """
        Attaches a proof file to the transaction and moves it to SUBMITTED state.
        """
        proof = PaymentProof.objects.create(
            transaction=transaction_obj,
            image=proof_image
        )
        
        # Once proof is uploaded, it moves to 'Under Review' or 'Submitted'
        transaction_obj.status = PaymentTransaction.Status.SUBMITTED
        transaction_obj.save()
        
        return proof
