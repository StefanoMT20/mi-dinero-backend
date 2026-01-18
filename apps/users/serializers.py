from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User."""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado que incluye datos del usuario en la respuesta."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
