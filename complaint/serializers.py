from rest_framework import serializers
from .models import Complaint
from Village.serializers import LocationSerializer

class ComplaintSerializer(serializers.ModelSerializer):
    
    village = LocationSerializer(read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['complaint_id', 'date_submitted', 'location', 'complainant']