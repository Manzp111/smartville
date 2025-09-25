from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema, OpenApiResponse,OpenApiResponse, OpenApiExample
from .models import Event
from .serializers import EventSerializer
from .utils import success_response, error_response
from rest_framework import permissions
from Resident.models import Resident
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from .mixins import EventRolePermissionMixin
from Resident.utils import get_resident_location
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Event
from Village.models import Village
from .serializers import EventSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Event
from .serializers import EventSerializer,VillageEventsResponseSerializer
from .models import STATUS_CHOICES, CATEGORY_CHOICES


class EventsByVillageAPIView(APIView):

    @extend_schema(
        summary="get village event only",
        request=None,  
        parameters=[
            OpenApiParameter(
                name="village_id",
                description="UUID of the village",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={200: VillageEventsResponseSerializer},
        examples=[
            OpenApiExample(
                "Village Events Response Example",
                description="Example response showing events for a village",
                
                value={
                    "village_id": "ed0da226-2a9d-4689-96b1-685f135a8bc9",
                    "village": "Gatenga",
                    "events": [
                        {
                            "event_id": "1c2eaa4f-54af-4a87-9b16-4f1c545f3d54",
                            "title": "Community Meeting",
                            "description": "Village-wide meeting",
                            "exact_place_of_village": "Near the market",
                            "date": "2025-09-20",
                            "start_time": "10:00:00",
                            "end_time": "12:00:00",
                            "organizer": 1,
                            "status": "APPROVED",
                            "image": None,
                            "created_at": "2025-09-15T08:00:00Z",
                            "updated_at": "2025-09-15T08:00:00Z",
                            "village": "Gatenga, Kicukiro, Kigali"
                        }
                    ]
                },
                response_only=True
            ),
        ],
    )
    def get(self, request, village_id):
        """
        GET /api/event/village/<uuid:village_id>/events/
        Returns all events for the given village_id (UUID).
        """
        try:
            village = Village.objects.get(village_id=village_id)
        except Village.DoesNotExist:
            return Response({"detail": "Village not found"}, status=status.HTTP_404_NOT_FOUND)

        events = Event.objects.filter(village=village,status="APPROVED").order_by("-date")
        event_serializer = EventSerializer(events, many=True)

        leader_data = None
        if village.leader:
            leader_data = {
                "user_id": village.leader.user_id,
                "first_name": village.leader.person.first_name,
                "last_name": village.leader.person.last_name,
                "email": village.leader.email,
                "phone_number": village.leader.person.phone_number,
            }

        response_data = {
            "success":True,
            "message":f"event of {village.village} of retrived well",
            "data":{
            
            "village": {
                "province":village.province,
                "district":village.district,
                "sector":village.sector,
                "cell":village.cell,
                "villages_name":village.village,
                "village_id": str(village.village_id),
                "village_leader":leader_data,
         
            },
            "events": event_serializer.data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)



from .pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
class EventViewSet(EventRolePermissionMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("-created_at")
    serializer_class = EventSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'category', 'date']
    search_fields = ['title', 'description', 'date']
    ordering = ['-created_at']
      
       
    

    def perform_create(self, serializer):
        user = self.request.user
        try:
            # Get the resident linked to this user
            resident = Resident.objects.get(person__user=user, is_deleted=False)
            village = resident.village
        except Resident.DoesNotExist:
            village = None  # or raise an error if you want to enforce a resident
        serializer.save(organizer=user, village=village)
    
    @extend_schema(
        
        summary="create event",
        description="if user created event it directly it automaticaly assigned to him as organizers and need the leader approval",
        request=EventSerializer,
        responses={
            201: OpenApiResponse(response=EventSerializer, description="Event created successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
           
                name="create event",
                value={
                     "title": "umuganda",
                    "description": "hari umuganda usoza ukwezi kuwa 30 kanama",
                    "exact_place_of_village": "uzabera kukagari",
                    "date": "2025-09-13",
                    "start_time": "16:53:40.782Z",
                    "end_time": "16:53:40.782Z",
                    "image": "none"
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
                message="Event created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Retrieve events according to requester role",
        description=(
            "Admins: access all events\n"
            "Leaders: access only their village events\n"
            "Residents: access only their own events\n"
            "Filters available: status, category\n"
        ),
        request=EventSerializer,
        responses={200: EventSerializer(many=True)},
        parameters=[
            # OpenApiParameter(
            #     name="status",
            #     description="Filter by event status",
            #     required=False,
            #     type=OpenApiTypes.STR,
            #     enum=[choice[0] for choice in STATUS_CHOICES],  # dropdown in Swagger
            # ),
            OpenApiParameter(
                name="category",
                description="Filter by event category",
                required=False,
                type=OpenApiTypes.STR,
                enum=[choice[0] for choice in CATEGORY_CHOICES],  # dropdown in Swagger
            ),
            OpenApiParameter(
                name="page",
                description="Page number for pagination",
                required=False,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name="limit",
                description="Number of items per page",
                required=False,
                type=OpenApiTypes.INT,
            ),

            OpenApiParameter(
                name="village_id",
                description="Filter by village UUID",
                required=False,
                type=OpenApiTypes.UUID,
            ),

        ],
        examples=[
            OpenApiExample(
                name="Example Event Response",
                value={
                    "success": True,
                    "message": "Events retrieved successfully",
                    "data": [
                        {
                            "title": "Community Cleanup",
                            "status": "APPROVED",
                            "category": "Cleanliness Drive",
                            "village": {
                                "village_id": "92bcb9ea-b084-4234-9ae7-22a67db3c018",
                                "village": "Gakeri"
                            },
                            "date": "2025-09-27",
                        }
                    ],
                    "meta": {
                        "page": 1,
                        "limit": 10,
                        "total_pages": 1,
                        "total_items": 1
                    }
                }
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Filtering
        status_filter = request.query_params.get("status")
        category_filter = request.query_params.get("category")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(         
                serializer.data
            )

        serializer = self.get_serializer(queryset, many=True)
        return {
            "success": True,
            "message": "Events retrieved successfully",
            "data": serializer.data,
            "meta": {
                "page": 1,
                "limit": len(serializer.data),
                "total_pages": 1,
                "total_items": len(serializer.data),
                "next": None,
                "previous": None
            }
        }
    @extend_schema(
        responses={200: EventSerializer},
        summary="retriving one even by id"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="Event retrieved successfully"
        )

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
            raise MethodNotAllowed("PUT", detail="Updating events is disabled.")



    @extend_schema(
        responses={200: OpenApiResponse(description="Event deleted successfully")},
        summary="delete event by id"

    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success":True,
            "message":"event deleted well",
        },
  
            status=status.HTTP_200_OK
        )
    @extend_schema(
        request=EventSerializer,  # request schema (all fields optional)
        summary="update event patially",
        responses={
            200: OpenApiResponse(response=EventSerializer, description="Event updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Forbidden - no permission"),
            404: OpenApiResponse(description="Event not found")
        },
        examples=[
            OpenApiExample(
                "Partial Update Example",
                description="Update only the event title and Village",
                value={
     
                        "title": "Updated Umuganda Event",
                        "description": "Updated description for the event",
                        "status": "APPROVED",
                        "category": "Festival & Celebration",
                        "type": "Alert",
                        "exact_place_of_village": "New exact location",
                        "date": "2025-09-25",
                        "start_time": "10:00:00",
                        "end_time": "12:00:00",
                        "village": {
                            "village_id": "ed0da226-2a9d-4689-96b1-685f135a8bc9",
                            "province": "Amajyaruguru",
                            "district": "Burera",
                            "sector": "Bungwe",
                            "cell": "Bungwe",
                            "village": "Updated Gatenga"
                        },
                        "organizer": {
                            "person": {
                            "first_name": "Maombi",
                            "last_name": "Updated Immacule",
                            "phone_number": "0781234567",
                            "national_id": 1234567890123456,
                            "gender": "female",
                            "person_type": "resident"
                            }
                        }


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
                        "Village": "Huye",
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
        # kwargs['partial'] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success":True,
            "message":"event updated",
            "data":serializer.data

            }, status=status.HTTP_200_OK)
        
    



 # user can set ?page=2
class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"   # user can set ?limit=5
    page_query_param = "page"        


import django_filters
from .models import Event

class EventFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    start_time_from = django_filters.TimeFilter(field_name="start_time", lookup_expr="gte")
    end_time_to = django_filters.TimeFilter(field_name="end_time", lookup_expr="lte")

    class Meta:
        model = Event
        fields = [
            "status",
            "category",
            "type",
            "organizer",
            "village",
        ]

from .models import TYPE_CHOICES
class EventViewSetlist(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list events of a specific village with filters, searching, and pagination
    """

    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter

    # Searching in text fields
    search_fields = ["title", "description", "exact_place_of_village"]

    # Ordering fields
    ordering_fields = ["date", "start_time", "end_time", "created_at"]
    ordering = ["-date"]

    @extend_schema(
        summary="Retrieve events of a specific village",
        description="Fetch events by village ID with advanced filtering, searching, and pagination.",
        parameters=[
            OpenApiParameter(
                name="status",
                description="Filter by event status",
                required=False,
                type=OpenApiTypes.STR,
                enum=[choice[0] for choice in STATUS_CHOICES],
            ),
            OpenApiParameter(
                name="category",
                description="Filter by event category",
                required=False,
                type=OpenApiTypes.STR,
                enum=[choice[0] for choice in CATEGORY_CHOICES],
            ),
            OpenApiParameter(
                name="type",
                description="Filter by event type",
                required=False,
                type=OpenApiTypes.STR,
                enum=[choice[0] for choice in TYPE_CHOICES],
            ),
            OpenApiParameter(name="date_from", description="Filter events starting from this date", type=OpenApiTypes.DATE),
            OpenApiParameter(name="date_to", description="Filter events up to this date", type=OpenApiTypes.DATE),
            OpenApiParameter(name="search", description="Search in title, description, or place", type=OpenApiTypes.STR),
            OpenApiParameter(name="ordering", description="Order by date/start_time/end_time/created_at", type=OpenApiTypes.STR),
            OpenApiParameter(name="page", description="Page number for pagination", type=OpenApiTypes.INT),
            OpenApiParameter(name="limit", description="Number of items per page", type=OpenApiTypes.INT),
        ],
    )
    def list(self, request, village_id=None, *args, **kwargs):
        """List events of a specific village with filters, search and pagination"""

        # ✅ Validate village
        try:
            village = Village.objects.get(village_id=village_id)
        except Village.DoesNotExist:
            return Response(
                {"success": False, "message": "Village not found", "data": [], "meta": {}},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ✅ Base queryset
        queryset = Event.objects.filter(village=village)

        # ✅ Apply filters, search, ordering
        queryset = self.filter_queryset(queryset)

        # ✅ Pagination
        paginator = EventPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)

        return Response({
            "success": True,
            "message": f"Events for village {village.village} retrieved successfully",
            "data": serializer.data,
            "meta": {
                "page": paginator.page.number,
                "limit": paginator.get_page_size(request),
                "total_pages": paginator.page.paginator.num_pages,
                "total_items": paginator.page.paginator.count,
            }
        }, status=status.HTTP_200_OK)
