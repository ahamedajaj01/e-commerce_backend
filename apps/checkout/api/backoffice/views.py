from rest_framework.views import APIView
from core.common.responses.formatters import success_response, error_response
from apps.users.permissions import IsBackofficeStaff
from .serializers import AdminCheckoutSessionSerializer
from ...models.session import CheckoutSession

class AdminCheckoutSessionListView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        sessions = CheckoutSession.objects.all()
        
        # Simple filters for staff
        status_filter = request.query_params.get('status')
        if status_filter:
            sessions = sessions.filter(status=status_filter)
            
        from core.utils.pagination import paginate_queryset
        paginated_qs, meta = paginate_queryset(sessions, page=int(request.query_params.get('page', 1)))
        
        serializer = AdminCheckoutSessionSerializer(paginated_qs, many=True)
        return success_response(data={"results": serializer.data, "meta": meta})

class AdminCheckoutSessionDetailView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request, session_id):
        try:
            session = CheckoutSession.objects.get(id=session_id)
            return success_response(data=AdminCheckoutSessionSerializer(session).data)
        except CheckoutSession.DoesNotExist:
            return error_response(message="Session not found", status_code=404)
