from rest_framework.views import APIView
from core.common.responses.formatters import success_response

class HealthCheckView(APIView):
    permission_classes = []
    
    def get(self, request):
        data = {
            "status": "healthy",
            "version": "1.0.0"
        }
        return success_response(data=data, message="System is up and running")
