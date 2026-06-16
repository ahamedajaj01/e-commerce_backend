from rest_framework import serializers
from .models.user import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'role', 
            'is_staff', 'is_superuser', 'is_active', 'is_email_verified',
            'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_active', 'last_login']
