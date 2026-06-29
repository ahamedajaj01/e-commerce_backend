from rest_framework import serializers
from ...models.session import CheckoutSession

class CheckoutSessionCreateSerializer(serializers.Serializer):
    """Input for creating a new checkout session."""
    # Customer Info
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)

    # Address
    province = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    street = serializers.CharField(max_length=255)
    instructions = serializers.CharField(max_length=500, required=False, allow_blank=True)

    # Choices
    shipping_rule_id = serializers.UUIDField()


class CheckoutSessionSerializer(serializers.ModelSerializer):
    """Output for displaying checkout session details (e.g. on payment page)."""
    total_days_min = serializers.SerializerMethodField()
    total_days_max = serializers.SerializerMethodField()

    class Meta:
        model = CheckoutSession
        fields = [
            'id', 'status', 'customer_name', 'customer_email', 'customer_phone',
            'shipping_province', 'shipping_district', 'shipping_city', 'shipping_street',
            'shipping_rule_title', 'shipping_fee', 'subtotal', 'total_price',
            'transit_days_min', 'transit_days_max', 'processing_days_max',
            'total_days_min', 'total_days_max',
            'created_at', 'expires_at'
        ]

    def get_total_days_min(self, obj):
        # Already calculated in service, but we'll show the combined value
        return obj.transit_days_min

    def get_total_days_max(self, obj):
        return obj.transit_days_max + obj.processing_days_max
