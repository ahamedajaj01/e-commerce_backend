from rest_framework.views import APIView
from rest_framework import status
from core.common.responses.formatters import success_response, error_response
from apps.users.permissions import IsBackofficeStaff
from apps.inventory.selectors.inventory_selectors import get_low_stock_variants, get_all_inventory
from apps.inventory.services.inventory_services import adjust_inventory
from apps.inventory.api.serializers import InventorySerializer, VariantSummarySerializer
from apps.catalog.models.product import ProductVariant

class AdminInventoryView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        product_type = request.query_params.get('type')
        search = request.query_params.get('search')
        
        # 1. Get Params for Pagination
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
        except (ValueError, TypeError):
            page = 1
            page_size = 20

        # 2. Fetch QuerySet with search
        inventory_qs = get_all_inventory(product_type=product_type, search=search)
        
        # 3. Paginate
        from core.utils.pagination import paginate_queryset
        paginated_qs, meta = paginate_queryset(inventory_qs, page=page, page_size=page_size)
        
        # 4. Serialize
        serialized_data = InventorySerializer(paginated_qs, many=True, context={'request': request}).data
        
        return success_response(data={
            "results": serialized_data,
            "meta": meta
        })


class AdminInventoryAdjustmentView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def post(self, request):
        variant_id = request.data.get('variant_id')
        
        # Sanitize prefixed IDs sent from the frontend list (e.g. "v-uuid")
        if isinstance(variant_id, str):
            if variant_id.startswith('v-'):
                variant_id = variant_id[2:]
            elif variant_id.startswith('mv-'):
                variant_id = variant_id[3:]

        movement_type = request.data.get('movement_type', 'IN')
        note = request.data.get('note', '')

        # Always cast quantity to int — request.data values can be strings
        try:
            quantity = int(request.data.get('quantity', 0))
        except (TypeError, ValueError):
            return error_response(message="Invalid quantity. Must be a whole number.", status_code=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return error_response(message="Quantity must be greater than 0.", status_code=status.HTTP_400_BAD_REQUEST)

        if not variant_id:
            return error_response(message="variant_id is required.", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return error_response(message="Variant not found.", status_code=status.HTTP_404_NOT_FOUND)

        updated_variant = adjust_inventory(
            variant=variant,
            quantity=quantity,
            movement_type=movement_type,
            note=note
        )

        return success_response(data={
            "variant_id": str(updated_variant.id),
            "sku": updated_variant.sku,
            "stock_quantity": updated_variant.stock_quantity,
            "movement_type": movement_type,
            "adjusted_by": quantity,
        })


class AdminLowStockView(APIView):
    permission_classes = [IsBackofficeStaff]
    
    def get(self, request):
        low_stock_variants = get_low_stock_variants()
        results = []
        for v in low_stock_variants:
            results.append({
                "id": str(v.id),
                "sku": v.sku,
                "product_name": v.product.name,
                "stock_quantity": v.stock_quantity,
            })
        return success_response(data=results)
