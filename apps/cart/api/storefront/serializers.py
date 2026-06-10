from rest_framework import serializers
from ...models.cart import Cart
from ...models.cart_item import CartItem
from apps.catalog.api.serializers import ProductVariantSerializer, ProductMediaSerializer

class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    thumbnail = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'product_name', 'thumbnail', 'quantity', 'subtotal']

    def get_thumbnail(self, obj):
        first_media = obj.variant.product.media.first()
        if first_media:
            return first_media.file.url
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

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0) # 0 means remove
