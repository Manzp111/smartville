from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # Safe image URL
    organizer = serializers.ReadOnlyField(source="organizer.email")
    status = serializers.CharField(read_only=True)  # Default: read-only for everyone

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
            "image_url",
            "status",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request") if self.context else None
        user = getattr(request, "user", None)
        # Leaders can update status
        if getattr(user, "role", None) == "leader":
            self.fields["status"].read_only = False

    def get_image_url(self, obj):
        request = self.context.get("request") if self.context else None
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
