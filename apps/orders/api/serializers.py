from rest_framework import serializers
from ..models import Order, OrderItem, OrderStatusHistory

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'previous_status', 'new_status', 'changed_by_name', 'notes', 'created_at']


class PublicStatusHistorySerializer(serializers.ModelSerializer):
    """Limited status history for public tracking (no staff info)."""
    class Meta:
        model = OrderStatusHistory
        fields = ['new_status', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'variant_id', 'product_name', 
            'variant_name', 'sku', 'price', 'quantity', 'line_total',
            'variant_image', 'image'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        
        # 1. Priority: Use the exact SNAPSHOT captured during order placement
        if obj.variant_image:
            url = obj.variant_image
            if request and not url.startswith('http'):
                return request.build_absolute_uri(url)
            return url

        # 2. Fallback: Use the product's current main thumbnail
        if obj.product_variant and obj.product_variant.product:
            first_media = obj.product_variant.product.media.first()
            if first_media and first_media.file:
                url = first_media.file.url
                if request and not url.startswith('http'):
                    return request.build_absolute_uri(url)
                return url
        return None


class OrderListSerializer(serializers.ModelSerializer):
    """Summarized view for lists."""
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    image = serializers.SerializerMethodField()
    customer_identity = serializers.CharField(source='customer_name', read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 
            'total_price', 'item_count', 'image', 'customer_identity', 
            'progress', 'created_at'
        ]

    def get_image(self, obj):
        first_item = obj.items.first()
        if first_item:
            return OrderItemSerializer(first_item, context=self.context).data.get('image')
        return None

    def get_progress(self, obj):
        progress_map = {
            Order.Status.PENDING: 20,
            Order.Status.CONFIRMED: 40,
            Order.Status.PROCESSING: 60,
            Order.Status.SHIPPED: 80,
            Order.Status.DELIVERED: 100,
            Order.Status.CANCELLED: 0
        }
        return progress_map.get(obj.status, 0)


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full detail view for buyers and staff."""
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    transactions = serializers.SerializerMethodField()
    
    # Combined ETA for display
    arrival_estimate = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'payment_method',
            'customer_name', 'customer_email', 'customer_phone',
            'shipping_province', 'shipping_district', 'shipping_city', 
            'shipping_street', 'shipping_instructions',
            'subtotal', 'shipping_fee', 'total_price',
            'transit_days_min', 'transit_days_max', 'processing_days_max',
            'arrival_estimate', 'items', 'status_history', 'transactions', 'created_at'
        ]

    def get_transactions(self, obj):
        from apps.payments.api.serializers import PaymentTransactionSerializer
        return PaymentTransactionSerializer(obj.transactions.all(), many=True, context=self.context).data

    def get_arrival_estimate(self, obj):
        min_days = obj.transit_days_min 
        max_days = obj.transit_days_max + obj.processing_days_max
        return f"{min_days}-{max_days} business days"


class OrderTrackingSerializer(serializers.ModelSerializer):
    """Anonymized tracking view for guest users."""
    status_timeline = PublicStatusHistorySerializer(source='status_history', many=True, read_only=True)
    arrival_estimate = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_number', 'status', 'payment_status', 
            'arrival_estimate', 'status_timeline', 'created_at'
        ]

    def get_arrival_estimate(self, obj):
        min_days = obj.transit_days_min 
        max_days = obj.transit_days_max + obj.processing_days_max
        return f"{min_days}-{max_days} business days"


class OrderStatusUpdateSerializer(serializers.Serializer):
    """For administrative status changes."""
    status = serializers.ChoiceField(choices=Order.Status.choices, required=False)
    payment_status = serializers.ChoiceField(choices=Order.PaymentStatus.choices, required=False)
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        if 'status' not in data and 'payment_status' not in data:
            raise serializers.ValidationError("Either 'status' or 'payment_status' must be provided.")
        return data
