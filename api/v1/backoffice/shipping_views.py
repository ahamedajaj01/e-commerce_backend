from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.common.responses.formatters import success_response, error_response
from apps.shipping.models.shipping import ShippingRule
from apps.shipping.serializers import ShippingRuleSerializer
from apps.users.permissions import IsBackofficeStaff


class AdminShippingRuleListView(generics.ListCreateAPIView):
    """
    GET  - List all shipping rules (ordered by priority)
    POST - Create a new shipping rule
    """
    serializer_class = ShippingRuleSerializer
    permission_classes = [IsBackofficeStaff]

    def get_queryset(self):
        return ShippingRule.objects.all().order_by('priority', 'province', 'district')


class AdminShippingRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    - Retrieve a single shipping rule
    PATCH  - Update a shipping rule (fee, title, area, active status)
    DELETE - Remove a shipping rule
    """
    serializer_class = ShippingRuleSerializer
    permission_classes = [IsBackofficeStaff]

    def get_queryset(self):
        return ShippingRule.objects.all()


class AdminShippingRuleToggleView(APIView):
    """
    POST /backoffice/shipping/rules/{id}/toggle/
    Quickly toggle the is_active status of a shipping rule.
    """
    permission_classes = [IsBackofficeStaff]

    def post(self, request, pk):
        try:
            rule = ShippingRule.objects.get(pk=pk)
        except ShippingRule.DoesNotExist:
            return error_response(message="Shipping rule not found", status_code=404)

        rule.is_active = not rule.is_active
        rule.save(update_fields=['is_active'])
        return success_response(
            data={'id': str(rule.id), 'is_active': rule.is_active},
            message=f"Rule {'activated' if rule.is_active else 'deactivated'} successfully"
        )
