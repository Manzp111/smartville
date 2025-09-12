# account/serializers.py
from rest_framework import serializers
from .models import Resident
from Location.models import Location
from account.models import Person

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'province', 'district', 'sector', 'cell', 'village']


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['person_id', 'first_name', 'last_name', 'national_id', 'phone_number', 'gender']


class ResidentSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    # Make location required on write, read_only is False now
    location = LocationSerializer() 

    class Meta:
        model = Resident
        fields = ['resident_id', 'person', 'location', 'added_by', 'has_account', 'is_deleted']
        read_only_fields = ['added_by', 'resident_id', 'has_account', 'is_deleted']  # These are set by the system

    def create(self, validated_data):
        """
        Custom create method to handle nested Person and Location objects.
        """
        # Extract nested data
        person_data = validated_data.pop('person')
        location_data = validated_data.pop('location')

        # 1. Get or Create Location? Or just create? Assuming creation for MVP.
        # For a robust solution, you might want to find an existing location.
        location, _ = Location.objects.get_or_create(**location_data)

        # 2. Create the Person
        person = Person.objects.create(**person_data)

        # 3. Get the user from the context (set by the View)
        user = self.context['request'].user

        # 4. Finally, create the Resident
        resident = Resident.objects.create(
            person=person,
            location=location,
            added_by=user,  # Set the user who is adding this resident
            **validated_data
        )
        return resident

    def update(self, instance, validated_data):
        """
        Custom update method to handle nested Person and Location updates.
        """
        person_data = validated_data.pop('person', None)
        location_data = validated_data.pop('location', None)

        # Update Location if provided
        if location_data:
            location_serializer = self.fields['location']
            location_serializer.update(instance.location, location_data)

        # Update Person if provided
        if person_data:
            person_serializer = self.fields['person']
            person_serializer.update(instance.person, person_data)

        # Update the resident instance itself
        return super().update(instance, validated_data)