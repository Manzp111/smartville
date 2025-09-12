from rest_framework import serializers
from .models import CommunityAlert

class CommunityAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityAlert
        fields = '__all__'
        read_only_fields = ['alert_id', 'created_at', 'location', 'reporter']