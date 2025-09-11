from rest_framework import viewsets, status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from event.models import Event
from event.serializers import EventSerializer
from event.utils import success_response, error_response

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("-created_at")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @extend_schema(
        responses={
            201: OpenApiResponse(response=EventSerializer, description="Event created successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        summary="create event"
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(
                data=serializer.data,
                message="Event created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        responses={200: EventSerializer(many=True)},
        summary="retrieve events"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message="Events retrieved successfully"
        )

    @extend_schema(
        responses={200: EventSerializer},
        summary="retrieve event by id"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="Event retrieved successfully"
        )

    @extend_schema(
        responses={200: EventSerializer},
        summary="update event by id"
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response(
                data=serializer.data,
                message="Event updated successfully"
            )
        return error_response(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        responses={204: OpenApiResponse(description="Event deleted successfully")},
        summary="delete event by id"
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(
            data=None,
            message="Event deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )

    @extend_schema(
        request=EventSerializer,
        summary="partially update event",
        responses={
            200: OpenApiResponse(response=EventSerializer, description="Event updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Forbidden - no permission"),
            404: OpenApiResponse(description="Event not found")
        },
        examples=[
            OpenApiExample(
                "Partial Update Example",
                description="Update only the event title and location",
                value={
                    "title": "Umuganda",
                    "location": "Huye campus "
                },
                request_only=True
            ),
            OpenApiExample(
                "Successful Update Response",
                description="Example of a successful event update response",
                value={
                    "status": "success",
                    "message": "Event updated successfully",
                    "data": {
                        "title": "umuganda",
                        "description": " umuganda w'ukwezi",
                        "location": "Huye",
                        "date": "2025-09-12",
                        "start_time": "09:00:00",
                        "end_time": "17:00:00",
                        "organizer": "gilbertnshimyimana130@gmail.com.com",
                        "image": None,
                        "created_at": "2025-09-11T08:30:00Z",
                        "updated_at": "2025-09-11T09:15:00Z"
                    }
                },
                response_only=True
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)