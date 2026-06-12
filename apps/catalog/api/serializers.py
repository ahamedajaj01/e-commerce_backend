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
        Safely handles remote cloud storage URLs (Cloudinary/S3) by not prefixing them.
        """
        if not obj.file:
            return None
        
        file_url = obj.file.url
        
        # If it's an absolute cloud URL already (starts with http/https), return it directly
        if file_url.startswith('http://') or file_url.startswith('https://'):
            return file_url
            
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(file_url)
            
        return file_url


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'name', 'size', 'color', 'price', 'stock_quantity']

class ProductStorefrontSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    media = serializers.SerializerMethodField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'base_price', 'category', 
            'material', 'sleeve', 'length', 'neck_line', 'fit',
            'is_visible', 'variants', 'media'
        ]

    def get_media(self, obj):
        return ProductMediaSerializer(obj.media.all(), many=True, context=self.context).data

class ProductBackofficeSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    media = serializers.SerializerMethodField()
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'base_price', 'category', 'category_detail',
            'material', 'sleeve', 'length', 'neck_line', 'fit',
            'is_active', 'is_visible', 'variants', 'media', 'created_at'
        ]

    def validate_name(self, value):
        from django.utils.text import slugify
        if len(slugify(value)) > 100:
            raise serializers.ValidationError("Product name is too long. Please shorten it to keep the URL slug small.")
        return value

    def get_media(self, obj):
        return ProductMediaSerializer(obj.media.all(), many=True, context=self.context).data
