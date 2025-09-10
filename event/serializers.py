from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source="organizer.email")

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "location",
            "date",
            "start_time",
            "end_time",
            "organizer",
            "image",
            "created_at",
            "updated_at",
        ]