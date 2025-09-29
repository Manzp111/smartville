# contacts/serializers.py
from rest_framework import serializers
from .models import Contact
from django.contrib.auth import get_user_model
from Village.models import Village
from Village.serializers import LocationSerializer
from account.serializers import UserListSerializer


# class VillageSerializer(serializers.ModelSerializer):
#     """Show village basic info if needed."""
#     class Meta:
#         model = Village
#         fields = ["", "name"]  # adjust fields depending on your Village model


class ContactSerializer(serializers.ModelSerializer):
    created_by = UserListSerializer(read_only=True)
    village = LocationSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = [
            "contact_id",
            "name",
            "phone",
            "category",
            "description",
            "village",
            "hours",
            "priority",
            "created_at",
            "updated_at",
            "created_by",
        ]
        read_only_fields = ["contact_id", "created_at", "updated_at", "created_by"]
