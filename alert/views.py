from rest_framework import viewsets, permissions, status
from .models import CommunityAlert
from .serializers import CommunityAlertSerializer
from account.models import Person
from event.utils import success_response, error_response

class CommunityAlertViewSet(viewsets.ModelViewSet):
    queryset = CommunityAlert.objects.all()
    serializer_class = CommunityAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        person = getattr(user, 'person', None)
        location = getattr(person, 'location', None)
        serializer.save(reporter=person, location=location)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(
                data=serializer.data,
                message="Alert submitted successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )