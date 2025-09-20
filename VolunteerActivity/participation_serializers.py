# VolunteerActivity/serializers.py

from rest_framework import serializers
from .models import VolunteerParticipation, VolunteeringEvent

class VolunteerParticipationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a participation request.
    Users can send 'event' and optional 'notes'.
    Validation ensures:
      - User cannot join twice
      - Event is in user's village
      - Event is approved
    """
    class Meta:
        model = VolunteerParticipation
        fields = ['event', 'notes']
# VolunteerActivity/participation_serializers.py

from rest_framework import serializers
from .models import VolunteerParticipation, VolunteeringEvent
from Village.serializers import LocationSerializer  # Assuming you have a VillageSerializer
from account.serializers import UserListSerializer  # Assuming you have a UserSerializer

class VolunteeringEventNestedSerializer(serializers.ModelSerializer):
    village = LocationSerializer()
    organizer = UserListSerializer()

    class Meta:
        model = VolunteeringEvent
        fields = [
            'volunteer_id', 'title', 'description', 'date', 'start_time', 'end_time',
            'capacity', 'village', 'organizer', 'status', 'location',
            'skills_required', 'category', 'created_at', 'updated_at', 'approved_at'
        ]


class VolunteerParticipationSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    event = VolunteeringEventNestedSerializer()

    class Meta:
        model = VolunteerParticipation
        fields = [
            'participation_id', 'user', 'event', 'status',
            'notes', 'joined_at', 'updated_at', 'approved_at'
        ]
        read_only_fields = ['participation_id', 'status', 'joined_at', 'updated_at', 'approved_at']


class VolunteerParticipationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerParticipation
        fields = ['event', 'notes']

    def validate(self, attrs):
        user = self.context['request'].user
        event = attrs['event']

        # Cannot join twice
        if event.participations.filter(user=user).exists():
            raise serializers.ValidationError("You cannot join this event twice.")

        # Must be in user's village
        user_village_ids = [res.village.id for res in getattr(user, 'residencies', user.residencies.none()).all()]
        if event.village.id not in user_village_ids:
            raise serializers.ValidationError("You cannot join an event outside your village.")

        # Event must be approved
        if event.status != 'APPROVED':
            raise serializers.ValidationError("You cannot join an event that is not approved.")

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        event = attrs['event']
        if event.organizer == user:
            raise serializers.ValidationError(
                {"event": "You cannot join your own event as a participant."}
            )
        # Rule 1: Cannot join twice
        if VolunteerParticipation.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError("You cannot join this event twice.")

        # Rule 2: Event must be in user's village
        user_village_ids = [res.village.id for res in getattr(user, 'residencies', []).all()]
        if event.village.id not in user_village_ids:
            raise serializers.ValidationError("You cannot join an event outside your village.")

        # Rule 3: Event must be approved
        if event.status != 'APPROVED':
            raise serializers.ValidationError("You cannot join an event that is not approved.")

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        participation, created = VolunteerParticipation.objects.get_or_create(
            user=validated_data['user'],
            event=validated_data['event'],
            defaults={'notes': validated_data.get('notes', '')}
        )
        return participation


class VolunteerParticipationSerializer(serializers.ModelSerializer):
    """
    Serializer for listing, viewing, and updating participations.
    """
    user = serializers.StringRelatedField(read_only=True)  # Shows user __str__
    event = serializers.StringRelatedField(read_only=True)  # Shows event __str__

    class Meta:
        model = VolunteerParticipation
        fields = [
            'participation_id',
            'user',
            'event',
            'status',
            'notes',
            'joined_at',
            'updated_at',
            'approved_at'
        ]
        read_only_fields = ['participation_id', 'user', 'joined_at', 'updated_at', 'approved_at']
