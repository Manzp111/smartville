# VolunteerActivity/participation_serializers.py

from rest_framework import serializers
from .models import VolunteerParticipation, VolunteeringEvent
from Village.serializers import LocationSerializer  # adjust to your actual Village serializer
from account.serializers import UserListSerializer  # adjust to your actual User serializer

# ---------------- Nested Event Serializer ----------------
class VolunteeringEventNestedSerializer(serializers.ModelSerializer):
    village = LocationSerializer(read_only=True)
    organizer = UserListSerializer(read_only=True)

    class Meta:
        model = VolunteeringEvent
        fields = [
            'volunteer_id', 'title', 'description', 'date', 'start_time', 'end_time',
            'capacity', 'village', 'organizer', 'status', 'location',
            'skills_required', 'category', 'created_at', 'updated_at', 'approved_at'
        ]


# ---------------- Participation Serializer ----------------
class VolunteerParticipationSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    event = VolunteeringEventNestedSerializer(read_only=True)

    class Meta:
        model = VolunteerParticipation
        fields = [
            'participation_id', 'user', 'event', 'status',
            'notes', 'joined_at', 'updated_at', 'approved_at'
        ]
        read_only_fields = ['participation_id', 'status', 'joined_at', 'updated_at', 'approved_at']


# ---------------- Create Participation Serializer ----------------
class VolunteerParticipationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerParticipation
        fields = ['event', 'notes']

    def validate(self, attrs):
        user = self.context['request'].user
        event = attrs['event']

        # Cannot join own event
        if event.organizer == user:
            raise serializers.ValidationError({"event": "You cannot join your own event as a participant."})

        # Cannot join twice
        if VolunteerParticipation.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError("You cannot join this event twice.")

        # Event must be approved
        if event.status != 'APPROVED':
            raise serializers.ValidationError("You cannot join an event that is not approved.")

        # Must belong to user's village
        user_village_ids = []
        if hasattr(user, 'person') and user.person:
            residencies = getattr(user.person, 'residencies', [])
            if hasattr(residencies, 'all'):
                residencies = residencies.all()  # queryset safe
            user_village_ids = [r.village.village_id for r in residencies]

        if event.village.village_id not in user_village_ids:
            raise serializers.ValidationError("You cannot join an event outside your village.")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        participation, _ = VolunteerParticipation.objects.get_or_create(
            user=user,
            event=validated_data['event'],
            defaults={'notes': validated_data.get('notes', '')}
        )
        return participation


from rest_framework import serializers

class BulkParticipationUpdateSerializer(serializers.Serializer):
    participation_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="List of participation UUIDs to update"
    )
    status = serializers.ChoiceField(choices=['APPROVED', 'REJECTED'])
