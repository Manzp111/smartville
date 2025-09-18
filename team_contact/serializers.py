from rest_framework import serializers
from .models import TeamMember, ContactMessage, ContactReply

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'

class ContactReplySerializer(serializers.ModelSerializer):
    replied_by_username = serializers.CharField(source='replied_by.username', read_only=True)
    class Meta:
        model = ContactReply
        fields = ['id', 'reply_message', 'replied_by', 'replied_by_username', 'replied_at']

class ContactMessageSerializer(serializers.ModelSerializer):
    replies = ContactReplySerializer(many=True, read_only=True)
    class Meta:
        model = ContactMessage
        fields = '__all__'