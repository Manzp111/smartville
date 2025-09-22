from rest_framework import serializers
from .models import Resident
from account.models import Person, User
from Village.models import Village


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['person_id', 'first_name', 'last_name', 'national_id',
                  'phone_number', 'gender', 'person_type', 'registration_date']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'phone_number', 'email', 'role', 'is_active', 'is_verified']


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ['village_id', 'province', 'district', 'sector', 'cell', 'village']


class ResidentDetailSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    village = VillageSerializer()
    added_by = UserSerializer()

    class Meta:
        model = Resident
        fields = [
            'resident_id', 'status', 'has_account',
            'person', 'village', 'added_by',
            'created_at', 'updated_at', 'is_deleted', 'deleted_at'
        ]
