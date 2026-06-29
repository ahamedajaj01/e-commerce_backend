from rest_framework import serializers
from ..models.inventory import StockMovement
from apps.catalog.models.product import ProductVariant

class VariantSummarySerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    is_media_product = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'name', 'size', 'price', 'image_url',
            'product_id', 'product_name',
            'is_media_product', 'product_type'
        ]

    def get_image_url(self, obj):
        # 1. Try variant-specific image
        image_obj = obj.image
        # 2. Fallback to product first media
        if not image_obj:
            image_obj = obj.product.media.all().first()
        
        if not image_obj or not image_obj.file:
            return None
            
        file_url = image_obj.file.url
        if file_url.startswith('http://') or file_url.startswith('https://'):
            return file_url
            
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(file_url)
        return file_url

    def get_is_media_product(self, obj):
        return False

    def get_product_type(self, obj):
        return "CATALOG_PRODUCT"

class InventorySerializer(serializers.ModelSerializer):
    variant = VariantSummarySerializer(source='*', read_only=True)
    available_quantity = serializers.IntegerField(source='stock_quantity', read_only=True)
    total_quantity = serializers.IntegerField(source='stock_quantity', read_only=True)
    is_unlimited = serializers.BooleanField(default=False, read_only=True)
    reserved_quantity = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'variant', 'available_quantity', 'reserved_quantity', 'is_unlimited', 'total_quantity', 'updated_at']

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = '__all__'
