from rest_framework import serializers
from Resident.models import Resident
from event.models import Event
from Location.models import Location
from account.serializers import UserListSerializer

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
        model = Location
        fields = ["village_id", "village", "cell", "sector", "district", "province", "leader"]
