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
    leader=UserSerializer(read_only=True)
    class Meta:
        model = Village
        fields = ['village_id', 'province', 'district', 'sector', 'cell', 'village',"leader"]


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

class ResidentDetailsSerializer(serializers.ModelSerializer):
    person = PersonSerializer()   
    user_id = serializers.SerializerMethodField() 
    added_by = UserSerializer()

    class Meta:
        model = Resident
        fields = [
            'user_id',
            'resident_id', 'status', 'has_account',
            'person','village','added_by',
            'created_at'
        ]
    def get_user_id(self, obj):
            user = User.objects.filter(person=obj.person).first()
            return user.user_id if user else None
