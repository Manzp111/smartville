# serializers.py
from rest_framework import serializers
from .models import Resident, Location
from Location.serializers import LocationSerializer
from account.models import Person, User



class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["person_id","first_name", "last_name", "phone_number","national_id","gender","person_type","registration_date"]
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class UserSerilaizer(serializers.ModelSerializer):
    person=PersonSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["user_id","person"]

class ResidentSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    location=LocationSerializer(read_only=True)
    added_by = UserSerilaizer(read_only=True)
    added_by_email = serializers.ReadOnlyField(source="added_by.email")
    person_name = serializers.ReadOnlyField(source="person.full_name")
    location_name = serializers.ReadOnlyField(source="location.village")

    class Meta:
        model = Resident
        fields = [
            "resident_id",
            "person",
            "person_name",
            "location",
            "location_name",
            "status",
            "has_account",
            "added_by",
            "added_by_email",
            "is_deleted",
            "deleted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["added_by", "added_by_email", "status", "is_deleted", "deleted_at", "created_at", "updated_at"]

class ResidentStatusSerializer(serializers.ModelSerializer):
    """Only used by leaders/admin to update status"""
    class Meta:
        model = Resident
        fields = ["status"]
