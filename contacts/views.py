# contacts/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer
from .permissions import IsLeaderOrAdmin
from drf_spectacular.utils import extend_schema, extend_schema_view


TAG = ["Village contacts"]


@extend_schema(
    summary="List all contacts",
    description="Retrieve all contacts. Optionally filter by `village_id` query parameter.",
    responses={200: ContactSerializer(many=True)},
    tags=TAG
)
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


@extend_schema(
    summary="Create a new contact",
    description="Create a contact. Only leaders or admins can create contacts.",
    request=ContactSerializer,
    responses={201: ContactSerializer},
    tags=TAG
)
class ContactCreateView(generics.CreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsLeaderOrAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Attach the user as `created_by`
        contact = serializer.save(created_by=request.user)

        return Response(
            {"status": "success", "message": "Contact created successfully", "data": self.get_serializer(contact).data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a village contact",
        description="Get contact by UUID.",
        responses={200: ContactSerializer},
        tags=TAG
    ),
    put=extend_schema(
        summary="Update a village contact",
        description="Update contact completely. Only leaders or admins can update.",
        request=ContactSerializer,
        responses={200: ContactSerializer},
        tags=TAG
    ),
    patch=extend_schema(
        summary="Partial update a village contact",
        description="Partial update contact. Only leaders or admins can update.",
        request=ContactSerializer,
        responses={200: ContactSerializer},
        tags=TAG
    ),
    delete=extend_schema(
        summary="Delete a village contact",
        description="Delete contact by UUID. Only leaders or admins can delete.",
        responses={204: None},
        tags=TAG
    )
)
class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsLeaderOrAdmin]
    lookup_field = "contact_id"  # ✅ use UUID instead of pk

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
        serializer.save()  # keep existing `created_by`
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
