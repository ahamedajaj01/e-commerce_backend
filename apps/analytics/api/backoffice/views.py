from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsBackofficeStaff
from core.common.responses.formatters import success_response
from ...selectors import AnalyticsSelector

class AnalyticsSummaryView(APIView):
    """
    GET /api/v1/backoffice/analytics/summary/
    Dashboard overview statistics for staff.
    """
    permission_classes = [IsAuthenticated, IsBackofficeStaff]

    def get(self, request):
        stats = AnalyticsSelector.get_summary_stats()
        return success_response(data=stats)
