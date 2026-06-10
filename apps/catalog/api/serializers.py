from rest_framework import serializers
from ..models.product import Product, Category, ProductVariant, ProductMedia

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'children']
        depth = 1

class ProductMediaSerializer(serializers.ModelSerializer):
    """
    Serialize product media with full image URLs.
    
    Converts relative file paths to absolute URLs that frontend can use directly.
    Example: 'products/media/image.jpg' -> '/media/products/media/image.jpg'
    """
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductMedia
        fields = ['id', 'media_type', 'file', 'file_url', 'sort_order', 'alt_text']
    
    def get_file_url(self, obj):
        """
        Generate full URL for media file.
        
        Returns:
            str: Full URL path to the media file (e.g., '/media/products/media/image.jpg')
                 or absolute URL if request context is available
        """
        if not obj.file:
            return None
        
        request = self.context.get('request')
        # Get the relative media path
        relative_path = obj.file.url
        
        if request:
            # Return absolute URL if request context is available
            return request.build_absolute_uri(relative_path)
        
        # Return relative URL otherwise
        return relative_path

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'name', 'size', 'color', 'price', 'stock_quantity']

class ProductStorefrontSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    media = ProductMediaSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'base_price', 'category', 
            'material', 'sleeve', 'length', 'neck_line', 'fit',
            'is_visible', 'variants', 'media'
        ]

class ProductBackofficeSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    media = ProductMediaSerializer(many=True, read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'base_price', 'category', 'category_detail',
            'material', 'sleeve', 'length', 'neck_line', 'fit',
            'is_active', 'is_visible', 'variants', 'media', 'created_at'
        ]
