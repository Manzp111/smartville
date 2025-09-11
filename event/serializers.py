from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
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
    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None