from rest_framework import serializers
from .models.user import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'role', 'is_staff', 'is_superuser', 'is_email_verified']
