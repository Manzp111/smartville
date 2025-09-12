# serializers.py
from rest_framework import serializers
from .models import Resident, Location

class ResidentSerializer(serializers.ModelSerializer):
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
