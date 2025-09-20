from rest_framework import viewsets, status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse
from event.models import EventAttendance
from event.serializers import EventAttendanceSerializer
from event.utils import success_response, error_response

class EventAttendanceViewSet(viewsets.ModelViewSet):
    queryset = EventAttendance.objects.all()
    serializer_class = EventAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={
            201: OpenApiResponse(response=EventAttendanceSerializer, description="Joined event successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        summary="join event"
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Joined event successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        responses={200: EventAttendanceSerializer(many=True)},
        summary="list event attendance"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message="Attendance records retrieved successfully"
        )

    @extend_schema(
        responses={200: EventAttendanceSerializer},
        summary="retrieve attendance record"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="Attendance record retrieved successfully"
        )

    @extend_schema(
        responses={204: OpenApiResponse(description="Attendance record deleted successfully")},
        summary="delete attendance record"
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(
            data=None,
            message="Attendance record deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )