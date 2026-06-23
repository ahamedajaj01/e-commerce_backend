from rest_framework import serializers
from .models.shipping import ShippingRule


# -----------------------------------------------------------
# Admin (Backoffice) Serializers
# -----------------------------------------------------------

class ShippingRuleSerializer(serializers.ModelSerializer):
    """
    Full CRUD serializer for the Admin panel.
    Updated to include granular transit day components.
    """
    class Meta:
        model = ShippingRule
        fields = [
            'id', 'title',
            'province', 'district', 'city_or_municipality',
            'shipping_fee', 
            'transit_days_min', 'transit_days_max', # New granular fields
            'estimated_days', # Descriptive string (Backward compatibility)
            'priority', 'is_default', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'priority', 'created_at', 'updated_at']

    def validate(self, data):
        # Enforce single default rule
        is_default = data.get('is_default', False)
        if is_default:
            existing_default = ShippingRule.objects.filter(is_default=True)
            # Exclude current instance when updating
            if self.instance:
                existing_default = existing_default.exclude(pk=self.instance.pk)
            if existing_default.exists():
                raise serializers.ValidationError(
                    "A default shipping rule already exists. Please deactivate the existing default first."
                )

        # Must have at least a province or be marked as default
        province = data.get('province', getattr(self.instance, 'province', ''))
        if not province and not is_default and not getattr(self.instance, 'is_default', False):
            raise serializers.ValidationError(
                "A shipping rule must have at least a Province, or be set as the Default rule."
            )

        return data


# -----------------------------------------------------------
# Storefront Serializers
# -----------------------------------------------------------

class ShippingCalculationRequestSerializer(serializers.Serializer):
    """
    Validates the address data sent by the frontend.
    Updated to accept product IDs to calculate combined delivery ETA.
    """
    province = serializers.CharField(required=False, allow_blank=True, default='')
    district = serializers.CharField(required=False, allow_blank=True, default='')
    city = serializers.CharField(required=False, allow_blank=True, default='')
    order_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # New: Allow frontend to pass product IDs in the cart
    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list
    )


class ShippingCalculationResponseSerializer(serializers.Serializer):
    """
    Formats the shipping result returned to the user during checkout.
    Updated with aggregate delivery data (Product + Shipping).
    """
    rule_id = serializers.CharField()
    title = serializers.CharField()
    fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Combined Summary (The "True" arrival date)
    arrival_estimate = serializers.CharField(required=False)
    
    # Granular components
    transit_days_min = serializers.IntegerField(read_only=True)
    transit_days_max = serializers.IntegerField(read_only=True)
    processing_days_max = serializers.IntegerField(read_only=True) # Max lag from cart
    
    # Original field (Stays for backward compatibility)
    estimated_days = serializers.CharField()
