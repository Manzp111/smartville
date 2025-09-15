from rest_framework import serializers
from account.models import Person
from .models import Visitor
from Resident.models import Resident

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["first_name", "last_name", "phone_number", "national_id", "gender"]

class VisitorSerializer(serializers.ModelSerializer):
    visitor_info = PersonSerializer()

    class Meta:
        model = Visitor
        fields = [
            "visitor_id",
            "visitor_info",
            "host",
            "visitor_location",
            "reason_for_visit",
            "arrival_date",
            "departure_date",
            "registered_date",
            "updated_at",
        ]
        read_only_fields = ["visitor_id", "registered_date", "updated_at"]

    def create(self, validated_data):
        person_data = validated_data.pop("visitor_info")
        person = Person.objects.create(**person_data)
        visitor = Visitor.objects.create(visitor_info=person, **validated_data)
        return visitor
