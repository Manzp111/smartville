from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Check if user is verified
        if not self.user.is_verified:
            raise serializers.ValidationError({
                "status": "error",
                "message": "Email not verified"
            })

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access": data["access"],
                "refresh": data["refresh"],
                "user": {
                    "id": self.user.user_id,
                    "email": self.user.email,
                    "role": self.user.role
                }
            }
        }
