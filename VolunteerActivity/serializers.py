from rest_framework import serializers
from .models import VolunteeringEvent, VolunteerParticipation
from Village.models import Village
from account.models import User


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ["province", "district", "sector", "cell", "village"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "phone_number", "role"]


class VolunteerParticipationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = VolunteerParticipation
        fields = ["id", "user", "event", "status", "joined_at"]
        read_only_fields = ["status", "joined_at"]


class VolunteeringEventSerializer(serializers.ModelSerializer):
    village = LocationSerializer(read_only=True)
    organizer = UserSerializer(read_only=True)
    approved_volunteers_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = VolunteeringEvent
        fields = [
            "id",
            "title",
            "description",
            "date",
            "capacity",
            "village",
            "organizer",
            "approved_volunteers_count",
            "is_full",
        ]


# Serializer for creating events (so organizer/village auto-fill)
class VolunteeringEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteeringEvent
        fields = ["title", "description", "date", "capacity"]
