# serializers.py
from rest_framework import serializers
from .models import Resident
from Village.models import Village
from Village.serializers import LocationSerializer
from account.models import Person, User


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["person_id","first_name", "last_name", "phone_number","national_id","gender","person_type","registration_date"]
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class UserSerilaizer(serializers.ModelSerializer):
    person=PersonSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["user_id","person"]

class ResidentSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    village=LocationSerializer(read_only=True)
    added_by = UserSerilaizer(read_only=True)
    added_by_email = serializers.ReadOnlyField(source="added_by.email")
    person_name = serializers.ReadOnlyField(source="person.full_name")
    location_name = serializers.ReadOnlyField(source="Village.village")
    # status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)


    class Meta:
        model = Resident
        fields = [
            "resident_id",
            "person",
            "person_name",
            "village",
            "location_name",
            "status",
            "has_account",
            "added_by",
            "added_by_email",
            "is_deleted",
            "deleted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["added_by", "added_by_email", "status", "is_deleted", "deleted_at", "created_at", "updated_at"]
    def create(self, validated_data):
            person_data = validated_data.pop('person')
            person = Person.objects.create(**person_data)
            Village = self.context.get('Village')
            user = self.context.get('user')
            return Resident.objects.create(person=person, Village=Village, added_by=user, **validated_data)
        
    def update(self, instance, validated_data):
            person_data = validated_data.pop('person', None)
            if person_data:
                # Update the nested Person object
                for attr, value in person_data.items():
                    setattr(instance.person, attr, value)
                instance.person.save()
            
            # Update Resident fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
                


class ResidentStatusSerializer(serializers.ModelSerializer):
    """Only used by leaders/admin to update status"""
    class Meta:
        model = Resident
        fields = ["status"]

