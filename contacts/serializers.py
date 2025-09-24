# contacts/serializers.py
from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "name", "phone_number", "role", "village", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]
