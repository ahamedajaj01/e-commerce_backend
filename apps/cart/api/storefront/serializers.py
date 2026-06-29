from rest_framework import serializers
from ...models.cart import Cart
from ...models.cart_item import CartItem
from apps.catalog.api.serializers import ProductVariantSerializer, ProductMediaSerializer

class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    selected_image_url = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'product_name', 'selected_image_url', 'quantity', 'subtotal']

    def get_selected_image_url(self, obj):
        # Priority 1: user-selected image
        if obj.selected_media and obj.selected_media.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.selected_media.file.url)
            return obj.selected_media.file.url
        # Priority 2: variant's default linked image
        if obj.variant and obj.variant.image and obj.variant.image.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.variant.image.file.url)
            return obj.variant.image.file.url
        # Priority 3: first product media
        try:
            media_list = list(obj.variant.product.media.all())
            if media_list:
                request = self.context.get('request')
                url = media_list[0].file.url
                return request.build_absolute_uri(url) if request else url
        except (AttributeError, IndexError):
            pass
        return None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    is_guest = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'status', 'is_guest', 'items', 'total_quantity', 'total_price']

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_price(self, obj):
        return sum(item.variant.price * item.quantity for item in obj.items.all())

class AddToCartSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    media_id = serializers.UUIDField(required=False, allow_null=True)

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0) # 0 means remove
