from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .models import CommunityAlert
from .serializers import CommunityAlertSerializer
from .utils import success_response, error_response
from rest_framework import permissions
from .mixins import AlertRolePermissionMixin
from django_filters.rest_framework import DjangoFilterBackend

class CommunityAlertViewSet(AlertRolePermissionMixin, viewsets.ModelViewSet):
    queryset = CommunityAlert.objects.all().order_by("-created_at")
    serializer_class = CommunityAlertSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'village', 'alert_type', 'urgency_level', 'incident_date']
    search_fields = ['title', 'description', 'alert_type']
    ordering = ['-created_at']

    @extend_schema(
        summary="Create alert",
        description="Automatically assigns the reporter and village based on the logged-in user.",
        request=CommunityAlertSerializer,
        responses={
            201: OpenApiResponse(response=CommunityAlertSerializer, description="Alert created successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                name="create alert",
                value={
                    "title": "Fire in the market",
                    "description": "A fire broke out in the village market.",
                    "alert_type": "emergency",
                    "urgency_level": "high",
                    "specific_location": "Market center",
                    "incident_date": "2025-09-16",
                    "incident_time": "14:30:00",
                    "allow_sharing": True,
                    "contact_phone": "0780000000",
                    "is_anonymous": False
                }
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(
                data=serializer.data,
                message="Alert created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Retrieve alerts according to user role",
        description="Admins see all, leaders see their village, residents see their own.",
        request=CommunityAlertSerializer,
        responses={200: CommunityAlertSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Alerts retrieved successfully")

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT", detail="Updating alerts is disabled.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(
            data=None,
            message="Alert deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )

    @extend_schema(
        request=CommunityAlertSerializer,
        summary="Partially update alert (status only for leader/admin)",
        responses={
            200: OpenApiResponse(response=CommunityAlertSerializer, description="Alert updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Forbidden - no permission"),
            404: OpenApiResponse(description="Alert not found")
        },
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().perform_update(request, *args, **kwargs)