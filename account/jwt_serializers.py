from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    username_field = 'phone_number'

    def validate(self, attrs):
        data = super().validate(attrs)

        # Check if user is verified
        if not self.user.is_verified:
            raise serializers.ValidationError({
                "status": "error",
                "message": "Phone number not verified"
            })

        return {
            "success": True,
            "message": "Login successful",
            "data": {  # <- remove this nested "data"
                "access": data["access"],
                "refresh": data["refresh"],
                "user": {
                    "id": str(self.user.user_id),
                    "phone_number": self.user.phone_number,
                    "role": self.user.role,
                }
            }
        }
