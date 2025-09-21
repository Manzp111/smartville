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



from rest_framework import serializers
from .models import VolunteeringEvent
from Village.models import Village

# Minimal event serializer used only for lists (excludes village to avoid repetition)
class VolunteeringEventListSerializer(serializers.ModelSerializer):
    organizer =UserListSerializer(read_only=True)# change to nested if you want more info

    class Meta:
        model = VolunteeringEvent
        # exclude village to avoid repeating full village for each event
        exclude = ['village']  
        read_only_fields = ('volunteer_id', 'created_at', 'updated_at', 'approved_at')

# Minimal village serializer (top-level)
class VillageMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ('village_id', 'village', 'province', 'district', 'sector', 'cell')
