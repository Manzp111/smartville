from rest_framework import serializers
from .models import Visitor
from Resident.models import Resident
from Resident.serializers import ResidentSerializer
from    Village.serializers import LocationSerializer

class VisitorSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(
        source="resident.person.first_name", read_only=True
    )
    village_name =LocationSerializer(read_only=True) 
    
    # serializers.CharField(
    #     source="village.get_full_address", read_only=True
    # )
    
    class Meta:
        model = Visitor
        fields = [
            "visitor_id",
            "resident",
            "resident_name",
            "name",
            "phone_number",
            "id_number",
            "purpose_of_visit",
            "expected_duration",
            "vehicle_info",
            "date",
            "time_in",
            "time_out",
            "village",
            "village_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "visitor_id",
            "resident",
            "resident_name",
            "village",
            "village_name",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")

        if not request or not hasattr(request.user, "person"):
            raise serializers.ValidationError("Request user must be associated with a person.")

        # Get the approved resident for this user
        resident_instance = Resident.objects.filter(
            person=request.user.person,
            status="APPROVED"
        ).first()

        if not resident_instance:
            raise serializers.ValidationError("Resident must be approved to add visitors.")

        # Auto-assign resident and village
        validated_data["resident"] = resident_instance
        validated_data["village"] = resident_instance.village

        return super().create(validated_data)
