from rest_framework import serializers
from .models import Event
from account.serializers import PersonSerializer
from Village.serializers import LocationSerializer
from account.models import User
# from account.serializers import UserListSerializer

class UserListSerializer(serializers.ModelSerializer):
    person=PersonSerializer(read_only=True)
    class Meta:
        model=User
        fields=["person"]



class EventSerializer(serializers.ModelSerializer):
    organizer=  UserListSerializer(read_only=True)   
    village=LocationSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()  # Safe image URL
    # organizer = serializers.ReadOnlyField(source="organizer.email")
    # status = serializers.CharField(read_only=True)  # Default: read-only for everyone

    class Meta:
        model = Event
        fields = [
            "event_id",
            "title",
            "description",
            "village",
            "exact_place_of_village",
            "date",
            "start_time",
            "end_time",
            "organizer",
            "image",
            "image_url",
            "status",
            "created_at",
            
        ]
        extra_kwargs={
        "id":{"read_only":True}
    }

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






class EventSerializer(serializers.ModelSerializer):
    village = serializers.StringRelatedField()  

    class Meta:
        model = Event
        fields = "__all__"

class VillageEventsResponseSerializer(serializers.Serializer):
    village_id = serializers.UUIDField()
    village = serializers.CharField()
    events = EventSerializer(many=True)


