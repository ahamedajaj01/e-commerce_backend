from rest_framework.views import APIView

from apps.catalog.selectors.product_selectors import (
    get_storefront_products, 
    get_active_categories,
    get_product_by_slug
)
from apps.catalog.api.serializers import ProductStorefrontSerializer, CategorySerializer
import uuid
from rest_framework import status
from core.common.responses.formatters import success_response, error_response

class ProductListView(APIView):
    permission_classes = []
    
    def get(self, request):
        # Extract filters from query parameters, ignoring empty or None values
        raw_filters = {
            'category': request.query_params.get('category'),
            'category_id': request.query_params.get('category_id'),
            'category_slug': request.query_params.get('category_slug'),
            'is_new': request.query_params.get('is_new'),
            'is_featured': request.query_params.get('is_featured'),
            'is_trending': request.query_params.get('is_trending'),
            'search': request.query_params.get('search'),
        }
        
        # Clean filters: only keep values that are not None and not empty strings
        filters = {k: v for k, v in raw_filters.items() if v}

        products = get_storefront_products(filters=filters)
        
        # Pass request context to serializer for building absolute URLs
        serializer = ProductStorefrontSerializer(
            products,
            many=True,
            context={'request': request}
        )
        return success_response(data=serializer.data)

class CategoryListView(APIView):
    permission_classes = []
    
    def get(self, request):
        categories = get_active_categories()
        serializer = CategorySerializer(categories, many=True)
        return success_response(data=serializer.data)

class ProductDetailView(APIView):
    permission_classes = []
    
    def get(self, request, slug):
        product = get_product_by_slug(slug)
        if not product:
            return error_response(message="Product not found", status_code=status.HTTP_404_NOT_FOUND)
        
        # Consider visibility if needed, but get_product_by_slug already checks is_active
        # and standard practice allows direct access via slug even if is_visible=False 
        # (e.g. for exclusive collection links)
        
        serializer = ProductStorefrontSerializer(
            product,
            context={'request': request}
        )
        return success_response(data=serializer.data)
