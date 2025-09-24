# contacts/serializers.py
from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):

    village = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Contact
        fields = ["id", "name", "phone_number", "role", "village"]
        read_only_fields = ["id", "village"]
