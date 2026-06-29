from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from ..models import PaymentMethod, PaymentProvider, PaymentTransaction, PaymentProof

class PaymentProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProvider
        fields = ['id', 'name', 'provider_type', 'is_active', 'configuration']

class PaymentMethodSerializer(serializers.ModelSerializer):
    """Publicly visible payment options."""
    qr_image = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'code', 'description', 'instructions', 
            'qr_image', 'payment_type', 'requires_proof'
        ]

    def get_qr_image(self, obj):
        if not obj.qr_image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.qr_image.url)
        return obj.qr_image.url

class AdminPaymentMethodSerializer(serializers.ModelSerializer):
    """Full management serializer for staff."""
    code = serializers.SlugField(
        validators=[UniqueValidator(queryset=PaymentMethod.objects.all())]
    )

    class Meta:
        model = PaymentMethod
        fields = '__all__'

class PaymentProofSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PaymentProof
        fields = ['id', 'image', 'image_url', 'uploaded_at']

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Full detail of a payment attempt."""
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    proofs = PaymentProofSerializer(many=True, read_only=True)

    order_id = serializers.UUIDField(source='order.id', read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'order', 'order_id', 'order_number', 'payment_method', 'payment_method_name',
            'amount', 'currency', 'status', 'transaction_reference', 
            'proofs', 'verified_at', 'admin_notes', 'created_at'
        ]

class TransactionInitSerializer(serializers.Serializer):
    """Request body for starting a payment."""
    order_id = serializers.UUIDField()
    payment_method_id = serializers.UUIDField()

class VerificationActionSerializer(serializers.Serializer):
    """Admin response for a payment audit."""
    approve = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')
