from rest_framework import serializers
from .models.shipping import ShippingRule


# -----------------------------------------------------------
# Admin (Backoffice) Serializers
# -----------------------------------------------------------

class ShippingRuleSerializer(serializers.ModelSerializer):
    """
    Full CRUD serializer for the Admin panel.
    Used for both listing all rules and creating/updating a single rule.
    """
    class Meta:
        model = ShippingRule
        fields = [
            'id', 'title',
            'province', 'district', 'city_or_municipality',
            'shipping_fee', 'estimated_days',
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
    Validates the address data sent by the frontend (extracted from Google Places).
    All geo fields are optional because the backend has hierarchical fallback.
    """
    province = serializers.CharField(required=False, allow_blank=True, default='')
    district = serializers.CharField(required=False, allow_blank=True, default='')
    city = serializers.CharField(required=False, allow_blank=True, default='')
    order_total = serializers.DecimalField(max_digits=12, decimal_places=2)


class ShippingCalculationResponseSerializer(serializers.Serializer):
    """
    Formats the shipping result returned to the user during checkout.
    """
    rule_id = serializers.CharField()
    title = serializers.CharField()
    fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = serializers.CharField()
