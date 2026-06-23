from rest_framework.views import APIView
from core.common.responses.formatters import success_response, error_response
from apps.shipping.serializers import (
    ShippingCalculationRequestSerializer,
    ShippingCalculationResponseSerializer
)
from apps.shipping.services.shipping_service import ShippingService
from apps.catalog.models.product import Product
from apps.cart.selectors.cart_selectors import get_cart_with_items, get_guest_cart_with_items
from apps.cart.api.storefront.views import _get_guest_token


class ShippingFeeCalculationView(APIView):
    """
    POST /api/v1/storefront/shipping/calculate/

    Hybrid Delivery Estimation:
    1. If product_ids are provided in the payload, use them.
    2. If NOT provided, automatically fetch the current user's active cart.
    3. Calculate total arrival ETA = Max(Product Prep) + Courier Transit.
    """
    permission_classes = []

    def post(self, request):
        serializer = ShippingCalculationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid data", data=serializer.errors)

        data = serializer.validated_data
        
        # 1. Fetch Shipping Rule & Basic Transit Time
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

        # 2. Logic: Identify Products (Explicit vs Automatic)
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            # Automatic Fallback: Get items from current active cart
            cart = None
            if request.user.is_authenticated:
                cart = get_cart_with_items(request.user)
            else:
                guest_token = _get_guest_token(request)
                cart = get_guest_cart_with_items(guest_token)
            
            if cart:
                # We use .all() to hit the prefetched items list if available
                items = cart.items.all()
                product_ids = [item.variant.product_id for item in items]

        # 3. Calculate Maximum Preparation Lag
        max_proc_min = 0
        max_proc_max = 0
        
        if product_ids:
            products = Product.objects.filter(id__in=product_ids)
            for p in products:
                max_proc_min = max(max_proc_min, p.processing_days_min)
                max_proc_max = max(max_proc_max, p.processing_days_max)

        # 4. Sum with Shipping Transit
        total_min = result.transit_days_min + max_proc_min
        total_max = result.transit_days_max + max_proc_max
        
        # 5. Result Formatting (Overwrite legacy field for instant UI update)
        if max_proc_max > 0:
            result.estimated_days = f"{total_min}-{total_max} business days"
            result.arrival_estimate = result.estimated_days
        else:
            result.arrival_estimate = result.estimated_days
        
        result.processing_days_max = max_proc_max

        response = ShippingCalculationResponseSerializer(result)
        return success_response(data=response.data)
