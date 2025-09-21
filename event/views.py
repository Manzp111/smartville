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

        events = Event.objects.filter(village=village).order_by("-date")
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




from rest_framework.permissions import IsAuthenticated, AllowAny
class EventViewSet(EventRolePermissionMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("-created_at")
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'village', 'date']
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
        summary="retiving event acoording to the requester if admin you aceess all if leader you access your villages",
        description="retriving list of event  according to user if role is admin he access both if he is leader he acess his own if residents only he acess his own only it is used by dashbord only",
        request=EventSerializer,
        responses={200: EventSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="retrive event according to the loged in user ",
                
                summary="example of event data to be retrived",
                value={
                    "title": "gukingira",
                    "description": "abaganga bazaza gukingira abana kumashuri",
                    "village": {
                        "village_id": "92bcb9ea-b084-4234-9ae7-22a67db3c018",
                        "province": "Amajyaruguru",
                        "district": "Burera",
                        "sector": "Bungwe",
                        "cell": "Bungwe",
                        "village": "Gakeri"
                    },
                    "exact_location": "kigali",
                    "date": "2025-09-27",
                    "start_time": "15:29:00",
                    "end_time": "22:34:00",
                    "organizer": {
                        "person": {
                        "first_name": "Ndacyayisenga",
                        "last_name": "Aloys",
                        "phone_number": "null"
                        }
                    },
                    "image": "null",
                    "image_url": "null",
                    "status": "PENDING",
                    "created_at": "2025-09-13T15:31:21.848041+02:00",


                }

            )
        ],
    )


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Events retrieved successfully")

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
            raise MethodNotAllowed("PUT", detail="Updating events is disabled.")


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(
            data=instance,
            message="Event deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
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
        return super().perform_update(request, *args, **kwargs)
    


class EventViewSetlist(viewsets.ViewSet):
     
    def list(self, request, village_id=None):
        """List volunteering events of a specific village"""
        try:
            village = Village.objects.get(village_id=village_id)
        except Village.DoesNotExist:
            return Response({"detail": "Village not found"}, status=status.HTTP_404_NOT_FOUND)

        volunter_activity = Event.objects.filter(village=village)
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("page_size", 10)  # allow custom page size
        result_page = paginator.paginate_queryset(volunter_activity, request)
        serializer = EventSerializer(volunter_activity, many=True)
        return paginator.get_paginated_response({
            "status": "success",
            "message": f"Events for village {village.village}",
            
            "count": len(serializer.data),
            "village":{
                "village_id":village.village_id,
                "province":village.province,
                "district":village.district,
                "sector":village.sector,
                "cell":village.cell,
                "village":village.village,
            },
            "data": serializer.data
        })