from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsBackofficeStaff
from core.common.responses.formatters import success_response, error_response
from ...selectors import PaymentSelector
from ...services.verification_service import VerificationService
from ..serializers import (
    PaymentTransactionSerializer, 
    VerificationActionSerializer,
    AdminPaymentMethodSerializer,
    PaymentProviderSerializer
)
from ...models import PaymentTransaction, PaymentMethod, PaymentProvider

class AdminPaymentProviderView(APIView):
    """
    GET/POST /api/v1/backoffice/payments/providers/
    Manage the technical engines behind payment methods.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        providers = PaymentProvider.objects.all()
        serializer = PaymentProviderSerializer(providers, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = PaymentProviderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, message="Provider created")
        return error_response(message="Invalid data", data=serializer.errors)


class AdminPaymentMethodView(APIView):
    """
    GET /api/v1/backoffice/payments/methods/
    POST /api/v1/backoffice/payments/methods/
    Manage checkout payment options.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        methods = PaymentMethod.objects.all().order_by('display_order')
        serializer = AdminPaymentMethodSerializer(methods, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = AdminPaymentMethodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, message="Payment method created")
        return error_response(message="Invalid data", data=serializer.errors)


class AdminPaymentMethodDetailView(APIView):
    """
    GET/PATCH/DELETE /api/v1/backoffice/payments/methods/{id}/
    Manage a specific payment option.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request, pk):
        try:
            method = PaymentMethod.objects.get(pk=pk)
            return success_response(data=AdminPaymentMethodSerializer(method).data)
        except PaymentMethod.DoesNotExist:
            return error_response(message="Not found", status_code=404)

    def patch(self, request, pk):
        try:
            method = PaymentMethod.objects.get(pk=pk)
            serializer = AdminPaymentMethodSerializer(method, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return success_response(data=serializer.data, message="Payment method updated")
            return error_response(message="Invalid data", data=serializer.errors)
        except PaymentMethod.DoesNotExist:
            return error_response(message="Not found", status_code=404)

    def delete(self, request, pk):
        try:
            method = PaymentMethod.objects.get(pk=pk)
            method.delete()
            return success_response(message="Payment method deleted")
        except PaymentMethod.DoesNotExist:
            return error_response(message="Not found", status_code=404)


class AdminTransactionListView(APIView):
    """
    GET /api/v1/backoffice/payments/transactions/
    Staff list for auditing and reviewing incoming payments.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        qs = PaymentSelector.get_all_transactions()
        
        # Filters
        filters = {
            'status': request.query_params.get('status'),
            'order_number': request.query_params.get('order_number'),
        }
        qs = PaymentSelector.filter_transactions(qs, filters)
        
        from core.utils.pagination import paginate_queryset
        paginated_qs, meta = paginate_queryset(qs, page=int(request.query_params.get('page', 1)))
        
        serializer = PaymentTransactionSerializer(paginated_qs, many=True)
        return success_response(data={"results": serializer.data, "meta": meta})


class AdminTransactionDetailView(APIView):
    """
    GET /api/v1/backoffice/payments/transactions/{id}/
    View specific transaction details and its proofs.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request, transaction_id):
        try:
            tx = PaymentSelector.get_transaction_by_id(transaction_id)
            return success_response(data=PaymentTransactionSerializer(tx).data)
        except PaymentTransaction.DoesNotExist:
            return error_response(message="Transaction not found", status_code=404)


class AdminTransactionVerifyView(APIView):
    """
    POST /api/v1/backoffice/payments/transactions/{id}/verify/
    Action to Approve or Reject a payment attempt.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def post(self, request, transaction_id):
        try:
            tx = PaymentSelector.get_transaction_by_id(transaction_id)
        except PaymentTransaction.DoesNotExist:
            return error_response(message="Transaction not found", status_code=404)
        
        serializer = VerificationActionSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid parameters", data=serializer.errors)
        
        updated_tx = VerificationService.verify_transaction(
            transaction_obj=tx,
            admin_user=request.user,
            approve=serializer.validated_data['approve'],
            notes=serializer.validated_data.get('notes', '')
        )
        
        return success_response(
            data=PaymentTransactionSerializer(updated_tx).data,
            message="Payment verification completed."
        )
