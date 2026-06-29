from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from core.common.responses.formatters import success_response, error_response
from ...selectors import PaymentSelector
from ...services.transaction_service import TransactionService
from ..serializers import (
    PaymentMethodSerializer, 
    PaymentTransactionSerializer, 
    TransactionInitSerializer,
    PaymentProofSerializer
)
from apps.orders.models import Order
from ...models import PaymentMethod, PaymentTransaction
from apps.cart.api.storefront.views import _get_guest_token


def _verify_order_access(order, request):
    """
    Ensures that the requester has the right to access this order
    (either as the authenticated owner or via the correct guest token).
    """
    if request.user.is_authenticated:
        return order.user == request.user
    
    # Guest logic: Check the session associated with the order
    guest_token = _get_guest_token(request)
    if not guest_token:
        return False
        
    try:
        session = order.checkout_session
        return str(session.guest_token) == str(guest_token)
    except:
        return False


class ActivePaymentMethodsView(APIView):
    """
    GET /api/v1/storefront/payments/methods/
    Displays all active ways a customer can pay.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        methods = PaymentSelector.get_active_methods()
        serializer = PaymentMethodSerializer(methods, many=True)
        return success_response(data=serializer.data)


class PaymentTransactionInitView(APIView):
    """
    POST /api/v1/storefront/payments/transactions/
    Starts a payment lifecycle for an order.
    """
    permission_classes = [AllowAny] # Allow guests to pay

    def post(self, request):
        serializer = TransactionInitSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid request", data=serializer.errors)
        
        data = serializer.validated_data
        
        # 1. Fetch Order
        try:
            order = Order.objects.get(id=data['order_id'])
        except Order.DoesNotExist:
            return error_response(message="Order not found", status_code=404)
        
        # 2. Verify Ownership (Secure check for Guests and Users)
        if not _verify_order_access(order, request):
            return error_response(message="Access denied", status_code=403)
        
        # 3. Fetch Method
        try:
            method = PaymentMethod.objects.get(id=data['payment_method_id'], is_active=True)
        except PaymentMethod.DoesNotExist:
            return error_response(message="Invalid payment method", status_code=400)
        
        # 4. Create Transaction
        tx = TransactionService.init_transaction(order=order, payment_method=method)
        
        return success_response(
            data=PaymentTransactionSerializer(tx).data,
            status_code=status.HTTP_201_CREATED
        )


class PaymentProofUploadView(APIView):
    """
    POST /api/v1/storefront/payments/transactions/{id}/proof/
    Submit screenshot evidence of manual payment.
    """
    permission_classes = [AllowAny]

    def post(self, request, transaction_id):
        try:
            tx = PaymentTransaction.objects.get(id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            return error_response(message="Transaction not found", status_code=404)
        
        # Verify Ownership
        if not _verify_order_access(tx.order, request):
            return error_response(message="Access denied", status_code=403)
        
        if 'image' not in request.FILES:
            return error_response(message="No image provided", status_code=400)
        
        proof = TransactionService.submit_proof(transaction_obj=tx, proof_image=request.FILES['image'])
        
        return success_response(
            data=PaymentProofSerializer(proof).data,
            message="Payment proof submitted successfully!"
        )
