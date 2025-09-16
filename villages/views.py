from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Location.models import Location
from Resident.models import Resident
from event.models import Event
from .serializers import ResidentSerializer, EventSerializer, LocationSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


class VillageNewsAPIView(APIView):

    @extend_schema(
        summary="Get Village Dashboard",
        description="Retrieve all related information of a specific village, including residents, events, and counts.",
        parameters=[
            OpenApiExample(
                "Village UUID Example",
                description="Use the UUID of the village in the URL",
                value="f138c017-e26d-418b-85c6-b2978e348e91"
            )
        ],
        responses={
            200: OpenApiExample(
                "Village Dashboard Response Example",
                description="Shows village info, total residents, total events, and serialized lists of residents and events.",
                value={
                    "success": True,
                    "message": "all information of Kirwa, Bugamba, Kinyababa, Burera, Amajyaruguru",
                    "village": {
                        "village_id": "f138c017-e26d-418b-85c6-b2978e348e91",
                        "village": "Kirwa",
                        "cell": "Bugamba",
                        "sector": "Kinyababa",
                        "district": "Burera",
                        "province": "Amajyaruguru",
                        "resident_count": 12
                    },
                    "total_residents": 12,
                    "total_events": 3,
                    "residents": [
                        {
                            "resident_id": "b0c2f840-1c59-4d47-b70f-2f0b616e8f5a",
                            "person": 1,
                            "status": "APPROVED",
                            "has_account": True,
                            "created_at": "2025-09-15T08:00:00Z"
                        }
                    ],
                    "events": [
                        {
                            "event_id": "1c2eaa4f-54af-4a87-9b16-4f1c545f3d54",
                            "title": "Community Meeting",
                            "description": "Village-wide meeting",
                            "date": "2025-09-20",
                            "start_time": "10:00:00",
                            "end_time": "12:00:00",
                            "status": "APPROVED"
                        }
                    ]
                }
            )
        }
    )
    def get(self, request, village_id):
        try:
            village = Location.objects.get(village_id=village_id)
        except Location.DoesNotExist:
            return Response({"success": False, "message": "Village not found"}, status=status.HTTP_404_NOT_FOUND)

        # Query related data
        residents = Resident.objects.filter(location=village, is_deleted=False)
        events = Event.objects.filter(village=village)

        # Serialize
        resident_serializer = ResidentSerializer(residents, many=True)
        event_serializer = EventSerializer(events, many=True)
        village_serializer = LocationSerializer(village)

        # Build response
        response_data = {

            "success": True,
            "message": f"all information of {village.village} retrived well",
            "data ": {
            "total_residents": residents.count(),
            "total_events": events.count(),        
            "village": village_serializer.data,
            "events": event_serializer.data,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
