from rest_framework import viewsets, permissions, status
from .models import Complaint
from .serializers import ComplaintSerializer
from account.models import Person
from event.utils import success_response, error_response

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        person = getattr(user, 'person', None)
        location = getattr(person, 'location', None)
        serializer.save(complainant=person, location=location)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(
                data=serializer.data,
                message="Complaint submitted successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )