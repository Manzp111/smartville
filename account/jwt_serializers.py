from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from account.models import User 
from Resident.models import Resident
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




class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='person.first_name', read_only=True)
    last_name = serializers.CharField(source='person.last_name', read_only=True)
    gender = serializers.CharField(source='person.gender', read_only=True)
    national_id = serializers.CharField(source='person.national_id', read_only=True)
    person_type = serializers.CharField(source='person.person_type', read_only=True)
    village = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "phone_number",
            "role",
            "is_verified",
            "first_name",
            "last_name",
            "gender",
            "national_id",
            "person_type",
            "village"
        ]
    def get_village(self, obj):
        """Return the village of this user if they are a resident."""
        resident = Resident.objects.filter(person=obj.person, is_deleted=False).first()
        if resident:
            return {
                "village_id": str(resident.village.village_id),
                "name": resident.village.village,
                "cell": resident.village.cell,
                "sector": resident.village.sector,
                "district": resident.village.district,
                "province": resident.village.province,
                "status": resident.status
            }
        return None

