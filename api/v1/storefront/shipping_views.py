from rest_framework.views import APIView
from core.common.responses.formatters import success_response, error_response
from apps.shipping.serializers import (
    ShippingCalculationRequestSerializer,
    ShippingCalculationResponseSerializer
)
from apps.shipping.services.shipping_service import ShippingService


class ShippingFeeCalculationView(APIView):
    """
    POST /api/v1/storefront/shipping/calculate/

    Accepts Google Places-extracted address components and returns
    the applicable shipping fee based on admin-configured rules.

    Matching hierarchy (first match wins):
        1. Province + District + City/Municipality
        2. Province + District
        3. Province only
        4. Default rule (if configured by admin)

    All geo fields are optional. If the address cannot be matched,
    the endpoint returns a 404 letting the frontend handle it gracefully.
    """
    permission_classes = []

    def post(self, request):
        serializer = ShippingCalculationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid address data", data=serializer.errors)

        data = serializer.validated_data
        result = ShippingService.calculate_fee(
            province=data.get('province', ''),
            district=data.get('district', ''),
            city=data.get('city', ''),
            order_total=data['order_total']
        )

        if not result:
            return error_response(
                message="Shipping is currently not available for this location.",
                status_code=404
            )

        response = ShippingCalculationResponseSerializer(result)
        return success_response(data=response.data)
