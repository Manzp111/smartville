from rest_framework import serializers
from .models import VolunteeringEvent, VolunteerParticipation
from Village.models import Village
from account.models import User
from django.utils import timezone


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ["province", "district", "sector", "cell", "village"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "phone_number", "role"]

############

from rest_framework import serializers
from .models import VolunteeringEvent, VolunteerParticipation
from Village.serializers import LocationSerializer
from account.serializers import UserListSerializer


class VolunteeringEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteeringEvent
        fields = [
            'title', 'description', 'date', 'start_time', 'end_time',
            'capacity', 'location', 'skills_required'
        ]

    def validate_date(self, value):
        if value < serializers.DateTimeField().to_representation(timezone.now().date()):
            raise serializers.ValidationError("Event date cannot be in the past")
        return value


class VolunteeringEventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    village = LocationSerializer(read_only=True)
    approved_volunteers_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    is_joinable = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    user_participation_status = serializers.SerializerMethodField()
    can_manage = serializers.SerializerMethodField()

    class Meta:
        model = VolunteeringEvent
        fields = [
            'volunteer_id', 'title', 'description', 'date', 'start_time', 'end_time',
            'capacity', 'village', 'organizer', 'status', 'rejection_reason',
            'location', 'skills_required', 'created_at', 'updated_at',
            'approved_volunteers_count', 'is_full', 'available_spots',
            'is_joinable', 'is_upcoming', 'user_participation_status',
            'can_manage'
        ]
        read_only_fields = ['status', 'rejection_reason', 'approved_at']

    def get_user_participation_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_user_participation_status(request.user)
        return None

    def get_can_manage(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_user_manage(request.user)
        return False


class VolunteerParticipationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = VolunteeringEventSerializer(read_only=True)
    can_manage = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerParticipation
        fields = [
            'id', 'user', 'event', 'status', 'notes',
            'joined_at', 'updated_at', 'approved_at', 'can_manage'
        ]
        read_only_fields = ['user', 'event', 'joined_at', 'updated_at', 'approved_at']

    def get_can_manage(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.event.can_user_manage(request.user)
        return False


class VolunteerParticipationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerParticipation
        fields = ['event', 'notes']


class EventApprovalSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(required=False, allow_blank=True)