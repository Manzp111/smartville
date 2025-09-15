from rest_framework import serializers
from Resident.models import Resident
from event.models import Event
from Location.models import Location


class ResidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resident
        fields = ["resident_id", "person", "status", "has_account", "created_at"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["event_id", "title", "description", "date", "start_time", "end_time", "status"]


class LocationSerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(read_only=True)

    class Meta:
        model = Location
        fields = ["village_id", "village", "cell", "sector", "district", "province", "leader_name"]
