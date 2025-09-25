from rest_framework import serializers

from rest_framework import serializers
from Village.models import Village
from account.models import User

class LocatePointSerializer(serializers.Serializer):
    latitude = serializers.FloatField(
        required=True,
        min_value=-90.0,
        max_value=90.0,
        help_text="Latitude must be between -90 and 90."
    )
    longitude = serializers.FloatField(
        required=True,
        min_value=-180.0,
        max_value=180.0,
        help_text="Longitude must be between -180 and 180."
    )




class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model =Village
        fields = ['village_id', 'province', 'district', 'sector', 'cell', 'village']




from rest_framework import serializers
from account.models import User, Person
from .models import Village

from Village.serializers import LocationSerializer

class PersonalSerializer(serializers.ModelSerializer):
     class Meta:
         model=Person
         fields=["first_name","last_name","national_id"]



    

class LeaderSerializer(serializers.ModelSerializer):
    person = PersonalSerializer()
    village= serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id', 'phone_number', 'email', 'role', 'is_active', 'person', 'village']

    # def get_full_name(self, obj):
    #     if obj.person:
    #         return f"{obj.person.first_name} {obj.person.last_name}"
    #     return None

    # def get_village(self, obj):
    #     villages = obj.led_villages.all() if hasattr(obj, 'led_villages') else []
    #     return [v.get_full_address() for v in villages]
    
    def get_village(self, obj):
        """
        Returns the village info for which the user is a leader.
        Uses LocationSerializer to nest the address details.
        """
        village = Village.objects.filter(leader=obj).first()
        if village:
            return LocationSerializer(village).data
        return None


class PromoteToLeaderSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    village_id = serializers.UUIDField()

    def validate(self, data):
        try:
            user = User.objects.get(user_id=data['user_id'])
            if hasattr(user, "led_villages"):
                raise serializers.ValidationError("This user is already a leader of another village")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        try:
            village = Village.objects.get(village_id=data['village_id'])
        except Village.DoesNotExist:
            raise serializers.ValidationError("Village does not exist")

        data['user'] = user
        data['village'] = village
        return data

    def save(self):
        user = self.validated_data['user']
        village = self.validated_data['village']

        user.role = 'leader'
        user.save()

        village.leader = user
        village.save()
        return user


class UpdateLeaderSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='person.first_name', required=False)
    last_name = serializers.CharField(source='person.last_name', required=False)
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'is_active']

    def update(self, instance, validated_data):
        person_data = validated_data.pop('person', {})
        if 'first_name' in person_data:
            instance.person.first_name = person_data['first_name']
        if 'last_name' in person_data:
            instance.person.last_name = person_data['last_name']
        instance.person.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
