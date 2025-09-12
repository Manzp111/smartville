from rest_framework import serializers
from .models import Event, EventAttendance
from account.models import Person
class EventSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    organizer = serializers.ReadOnlyField(source="organizer.email")

    class Meta:
        model = Event
        fields = [
            "event_id",
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
    extra_kwargs = {
    "event_id": {"read_only": True}
}
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id',"first_name","last_name"]



class EventAttendanceSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    class Meta:
        model = EventAttendance
        fields = ['id', 'event', 'person__id', 'joined_at']
        read_only_fields = ['id', 'joined']