"""
Catalog API Views for products and categories.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.catalog.models.product import Product, Category, ProductVariant, ProductMedia
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for product categories.
    
    Endpoints:
        GET /api/v1/categories/ - List all categories
        POST /api/v1/categories/ - Create new category
        GET /api/v1/categories/{id}/ - Retrieve category details
        PUT /api/v1/categories/{id}/ - Update category
        DELETE /api/v1/categories/{id}/ - Delete category
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for products with image serving.
    
    Endpoints:
        GET /api/v1/products/ - List all products
        POST /api/v1/products/ - Create new product
        GET /api/v1/products/{id}/ - Retrieve product details with images
        PUT /api/v1/products/{id}/ - Update product
        DELETE /api/v1/products/{id}/ - Delete product
        GET /api/v1/products/{id}/images/ - Get product images
    
    Image URLs:
        All images are returned with full URLs (e.g., /media/products/media/image.jpg)
        which can be used directly by the frontend.
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        'media',
        'variants',
        'category'
    )
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    filterset_fields = ['category']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        
        - list: Returns ProductListSerializer (basic info with media)
        - retrieve: Returns ProductDetailSerializer (full info with variants)
        - default: Returns ProductDetailSerializer
        """
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_serializer_context(self):
        """Add request context to serializer for building absolute URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def images(self, request, pk=None):
        """
        Get all images for a product.
        
        Endpoint:
            GET /api/v1/products/{id}/images/
        
        Response:
            {
                "images": [
                    {
                        "id": 1,
                        "media_type": "IMAGE",
                        "file": "products/media/image.jpg",
                        "file_url": "/media/products/media/image.jpg",
                        "alt_text": "Product image"
                    }
                ]
            }
        """
        product = self.get_object()
        media = product.media.all()
        
        from .serializers import ProductMediaSerializer
        serializer = ProductMediaSerializer(
            media,
            many=True,
            context={'request': request}
        )
        
        return Response(
            {'images': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def featured(self, request):
        """
        Get featured products.
        
        Endpoint:
            GET /api/v1/products/featured/
        
        Returns products with images ready to display.
        """
        products = self.get_queryset()[:12]  # Get first 12 products
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
