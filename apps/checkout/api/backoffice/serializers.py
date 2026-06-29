from rest_framework import serializers
from ...models.session import CheckoutSession

class AdminCheckoutSessionSerializer(serializers.ModelSerializer):
    """Full detail serializer for staff auditing."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = CheckoutSession
        fields = '__all__'
