from rest_framework import serializers
from Resident.models import Resident
from event.models import Event
from Village.models import Village
from account.serializers import UserListSerializer
from VolunteerActivity.models import VolunteeringEvent,VolunteerParticipation

class ResidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resident
        fields = ["resident_id", "person", "status", "has_account", "created_at"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["event_id", "title", "description", "date", "start_time", "end_time", "status"]




      

class LocationSerializer(serializers.ModelSerializer):
    leader= UserListSerializer()

    class Meta:
        model = Village
        fields = ["village_id", "village", "cell", "sector", "district", "province", "leader"]


class VolunteeringEventSerializer(serializers.ModelSerializer):
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
            "approved_volunteers_count",
            "is_full",
        ]