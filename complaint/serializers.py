from rest_framework import serializers
from .models import Complaint
from Village.serializers import LocationSerializer
from account.models import User 
from account.serializers import PersonSerializer

class UserSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['user_id','email','role','phone_number','person']

class ComplaintSerializer(serializers.ModelSerializer):
    
    location = LocationSerializer(read_only=True)
    complainant = UserSerializer(read_only=True)

    class Meta:
        model = Complaint
        fields = [
            "complaint_id", "complainant", "description", "is_anonymous",
            "location", "date_submitted", "status"
        ]
        read_only_fields = ["complaint_id", "complainant", "location", "date_submitted"]

        