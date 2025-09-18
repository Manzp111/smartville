from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings
from .models import TeamMember, ContactMessage, ContactReply
from .serializers import TeamMemberSerializer, ContactMessageSerializer, ContactReplySerializer
from .tasks import send_contact_reply_email

class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all().order_by('-created_at')
    serializer_class = TeamMemberSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def replies(self, request, pk=None):
        message = self.get_object()
        serializer = ContactReplySerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(message=message, replied_by=request.user)
            # Send email notification to the original sender
            subject = f"Reply to your inquiry: {message.inquiry_type.title()}"
            email_message = (
                f"Dear {message.name},\n\n"
                f"Thank you for contacting us. Here is our reply to your message:\n\n"
                f"Your message:\n{message.message}\n\n"
                f"Our reply:\n{reply.reply_message}\n\n"
                f"Best regards,\nSmart Village Team"
            )
            send_contact_reply_email.delay(subject, email_message, message.email)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)