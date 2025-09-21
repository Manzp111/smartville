# VolunteerActivity/serializers.py
from rest_framework import serializers
from .models import VolunteeringEvent
from Village.serializers import LocationSerializer  # for village details
from account.serializers import PersonSerializer 
from account.serializers import UserListSerializer    # for organizer details

class VolunteeringEventSerializer(serializers.ModelSerializer):
    # Use nested serializers for organizer and village
    village = LocationSerializer(read_only=True)
    organizer =UserListSerializer(read_only=True)

    class Meta:
        model = VolunteeringEvent
        fields = [
            'volunteer_id',
            'title',
            'description',
            'date',
            'start_time',
            'end_time',
            'capacity',
            'village',
            'organizer',
            'status',
            'location',
            'skills_required',
            'category',
            'created_at',
            'updated_at',
            'approved_at'
        ]

class VolunteeringEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteeringEvent
        fields = [
            'title',
            'description',
            'date',
            'start_time',
            'end_time',
            'capacity',
            'village',  # this should be a PK when creating
            'skills_required',
            'category'
        ]

