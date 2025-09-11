# account/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .models import Resident
from .serializers import ResidentSerializer
from Location.models import Location
from .serializers import LocationSerializer
from rest_framework.decorators import action

# Import the new utility functions
from event.utils import success_response, error_response

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    list=extend_schema(
        summary="List all available locations",
        description="Retrieve a paginated list of all provinces, districts, sectors, cells, and villages. Use the `filter_by/` endpoint to narrow down the list hierarchically.",
        responses={
            200: OpenApiTypes.OBJECT, # You can create a more specific response schema if needed
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific location",
        description="Get the detailed information of a single location by its ID.",
        responses={
            200: LocationSerializer,
            404: OpenApiTypes.OBJECT
        }
    )
)
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing locations (Provinces, Districts, Sectors, Cells, Villages).
    Supports hierarchical filtering via the `filter_by` action.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def list(self, request, *args, **kwargs):
        """Override the list method to use consistent response"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return success_response(data=serializer.data, message="Locations retrieved successfully")
        except Exception as e:
            return error_response(message="Failed to retrieve locations", errors=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """Override the retrieve method to use consistent response"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(data=serializer.data, message="Location retrieved successfully")
        except Exception as e:
            return error_response(message="Location not found", errors=str(e), status_code=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        # ... [Your existing @extend_schema details remain the same] ...
    )
    @action(detail=False, methods=['get'])
    def filter_by(self, request):
        """Use consistent response for the custom action"""
        try:
            params = request.query_params
            queryset = self.get_queryset()
            for field in ['province', 'district', 'sector', 'cell']:
                if field in params:
                    queryset = queryset.filter(**{field: params[field]})
            serializer = self.get_serializer(queryset, many=True)
            return success_response(data=serializer.data, message="Locations filtered successfully")
        except Exception as e:
            return error_response(message="Filtering failed", errors=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="List residents added by the current user",
        description="Retrieves a list of all residents that the currently authenticated user has added to the system, including themselves.",
        responses={200: ResidentSerializer(many=True)}
    ),
    create=extend_schema(
        summary="Register a new resident",
        description="Creates a new Resident and linked Person record. The current user is automatically set as the `added_by` field.",
        request=ResidentSerializer,
        responses={201: ResidentSerializer}
    ),
    # ... [Other @extend_schema definitions] ...
)
class ResidentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Residents. Users can only see and manage residents they have added.
    """
    queryset = Resident.objects.all()
    serializer_class = ResidentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Resident.objects.filter(added_by=user) | Resident.objects.filter(person=user.person)

    def list(self, request, *args, **kwargs):
        """Consistent response for listing residents"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return success_response(data=serializer.data, message="Residents retrieved successfully")
        except Exception as e:
            return error_response(message="Failed to retrieve residents", errors=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """Consistent response for creating a resident"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return success_response(
                data=serializer.data, 
                message="Resident registered successfully", 
                status_code=status.HTTP_201_CREATED
            )
        except serializers.ValidationError as e:
            # Catch validation errors and format them nicely
            return error_response(
                message="Validation failed", 
                errors=e.detail, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return error_response(
                message="Failed to create resident", 
                errors=str(e), 
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """Consistent response for retrieving a single resident"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(data=serializer.data, message="Resident retrieved successfully")
        except Exception as e:
            return error_response(message="Resident not found", errors=str(e), status_code=status.HTTP_404_NOT_FOUND)

    # You can similarly override update, partial_update, and destroy methods
    def destroy(self, request, *args, **kwargs):
        """Consistent response for deleting (soft delete) a resident"""
        try:
            instance = self.get_object()
            instance.is_deleted = True  # Assuming a soft delete
            instance.save()
            return success_response(message="Resident deleted successfully", status_code=status.HTTP_200_OK)
        except Exception as e:
            return error_response(message="Failed to delete resident", errors=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)