from rest_framework import serializers
from .models import CommunityAlert
from account.serializers import PersonSerializer
from Village.serializers import LocationSerializer
from account.models import User

class UserListSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["person"]

class CommunityAlertSerializer(serializers.ModelSerializer):
    reporter = UserListSerializer(read_only=True)
    village = LocationSerializer(read_only=True)

    class Meta:
        model = CommunityAlert
        fields = [
            "alert_id",
            "title",
            "description",
            "alert_type",
            "urgency_level",
            "status",
            "reporter",
            "village",
            "specific_location",
            "incident_date",
            "incident_time",
            "allow_sharing",
            "contact_phone",
            "is_anonymous",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reporter", "created_at", "updated_at",  "village"]
    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user

        # Only allow leaders and admins to write status
        if not user.is_authenticated or user.role not in ["leader", "admin"]:
            fields["status"].read_only = True

        return fields

    def create(self, validated_data):
        user = self.context["request"].user
        # Get the user's village (assume Resident model links user to village)
        from Resident.models import Resident
        try:
            resident = Resident.objects.get(person__user=user, is_deleted=False)
            village = resident.village
        except Resident.DoesNotExist:
            raise serializers.ValidationError("You must be assigned to a village to report an alert.")
        validated_data["reporter"] = user
        validated_data["village"] = village
        return super().create(validated_data)