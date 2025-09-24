# contacts/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer
from .permissions import IsLeaderOrAdmin


class ContactListView(generics.ListAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = []  # Anyone can view

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        village_id = request.query_params.get("village_id")
        if village_id:
            queryset = queryset.filter(village_id=village_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"status": "success", "message": "Contacts retrieved", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class ContactCreateView(generics.CreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsLeaderOrAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user, village=request.user.village)
        return Response(
            {"status": "success", "message": "Contact created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsLeaderOrAdmin]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {"status": "success", "message": "Contact details retrieved", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"status": "success", "message": "Contact updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"status": "success", "message": "Contact deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
