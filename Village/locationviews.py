from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .serializers import LocatePointSerializer
import shapefile
from shapely.geometry import Point, shape
import os
from event.utils import success_response, error_response
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from shapely.geometry import Point, shape
import shapefile, os
from event.utils import success_response, error_response
from .models import Village
from Resident.models import Resident
from Resident.serializers import ResidentSerializer
from rest_framework.permissions import IsAuthenticated

from Resident.tasks import notify_village_leader_new_resident

class LocatePointAPIView(APIView):
    

    @extend_schema(
        summary="Locate village by coordinates",
        description="""Find the corresponding village, cell, sector, district, and province 
        for a given latitude and longitude point using shapefile data.""",
        request=LocatePointSerializer,
        examples=[
            OpenApiExample(
                "Valid Point Example",
                summary="Example of a point inside Rwanda",
                value={"latitude": -1.3782236, "longitude": 29.8094301},
                request_only=True
            ),
            OpenApiExample(
                "Invalid Point Example", 
                summary="Example of a point outside Rwanda",
                value={"latitude": 0.0, "longitude": 0.0},
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Village Village found successfully",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "success": True,
                            "message": "Village found successfully",
                            "data": {
                                "province": "Amajyaruguru",
                                "district": "Burera",
                                "sector": "Kinyababa",
                                "cell": "Bugamba",
                                "village": "Kirwa"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Validation Error",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={
                            "success": False,
                            "message": "error occurd",
                            "errors": {
                                "latitude": ["This field is required."],
                                "longitude": ["This field is required."]
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Village Not Found",
                examples=[
                    OpenApiExample(
                        "Not Found Error",
                        value={
                            "success": False,
                            "message": "Point is not inside any village polygon",
                            "errors": None,
                            "data": None
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Server Error",
                examples=[
                    OpenApiExample(
                        "Server Error",
                        value={
                            "success": False,
                            "message": "Failed to process Village data",
                            "errors": "Shapefile not found or corrupted"
                        }
                    )
                ]
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = LocatePointSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="error occured contact gilbert",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]

        try:
            # Adjust the path to your shapefile
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            shp_path = os.path.join(BASE_DIR, "Village level boundary", "RWA_adm5.shp")

            # Check if shapefile exists
            if not os.path.exists(shp_path):
                return error_response(
                    message="Village data not available",
                    errors="Shapefile not found",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            sf = shapefile.Reader(shp_path)
            point = Point(longitude, latitude)
            village_info = None

            for record, shp in zip(sf.records(), sf.shapes()):
                polygon = shape(shp.__geo_interface__)
                if polygon.contains(point):
                    village_info = {
                        "province": record[4],
                        "district": record[6],
                        "sector": record[8],
                        "cell": record[10],
                        "village": record[12],
                    }
                    break

            if village_info:
                return success_response(
                    data=village_info,
                    message="Village found successfully",
                    status_code=status.HTTP_200_OK
                )
            else:
                return error_response(
                    message="Point is not inside any village polygon",
                    status_code=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            return error_response(
                message="Failed to process Village data",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class JoinVillageByCoordinatesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Join a village using GPS coordinates",
        description="""
        This endpoint allows a user to automatically join a village based on the provided 
        latitude and longitude. The system locates the corresponding village using shapefile data, 
        checks if the user is already a resident, and creates a resident record in PENDING status. 
        Village leaders are notified asynchronously.
        """,
        request=LocatePointSerializer,
        examples=[
            OpenApiExample(
                "Valid Point Example",
                summary="Point inside Rwanda",
                value={"latitude": -1.3782236, "longitude": 29.8094301},
                request_only=True
            ),
            OpenApiExample(
                "Invalid Point Example",
                summary="Point outside Rwanda",
                value={"latitude": 0.0, "longitude": 0.0},
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(
                description="Resident join request created successfully",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Success Example",
                        value={
                            "success": True,
                            "message": "Join request submitted successfully. Waiting for leader approval.",
                            "data": {
                                "id": "uuid-of-resident",
                                "person": "uuid-of-person",
                                "Village": {
                                    "village_id": "uuid-of-Village",
                                    "province": "Amajyaruguru",
                                    "district": "Burera",
                                    "sector": "Kinyababa",
                                    "cell": "Bugamba",
                                    "village": "Kirwa",
                                    "leader": "uuid-of-leader"
                                },
                                "status": "PENDING",
                                "added_by": "uuid-of-user",
                                "created_at": "2025-09-13T10:00:00Z",
                                "updated_at": "2025-09-13T10:00:00Z"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Validation Error of un identified longitude and latitude",
                examples=[
                    OpenApiExample(
                        "Missing Fields Example",
                        value={
                            "success": False,
                            "message": "Missing required Village fields: latitude, longitude",
                            "errors": None
                        }
                    ),
                    OpenApiExample(
                        "No Person Record Example",
                        value={
                            "success": False,
                            "message": "No person record for the user",
                            "errors": None
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Point not inside any village polygon",
                examples=[
                    OpenApiExample(
                        "Not Found Example",
                        value={
                            "success": False,
                            "message": "Point is not inside any village polygon",
                            "errors": None,
                            "data": None
                        }
                    )
                ]
            ),
            409: OpenApiResponse(
                description="User already a resident in another village",
                examples=[
                    OpenApiExample(
                        "Conflict Example",
                        value={
                            "success": False,
                            "message": "You are already a resident in Kirwa village in Kinyababa sector",
                            "errors": None
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Server Error",
                examples=[
                    OpenApiExample(
                        "Server Error Example",
                        value={
                            "success": False,
                            "message": "Failed to process Village data",
                            "errors": "Shapefile not found or corrupted"
                        }
                    )
                ]
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = LocatePointSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="error contact gilbert",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]

        # Load shapefile
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        shp_path = os.path.join(BASE_DIR, "Village level boundary", "RWA_adm5.shp")
        if not os.path.exists(shp_path):
            return error_response("Village data not available", errors="Shapefile not found", status_code=500)

        sf = shapefile.Reader(shp_path)
        point = Point(longitude, latitude)
        village_info = None

        for record, shp in zip(sf.records(), sf.shapes()):
            polygon = shape(shp.__geo_interface__)
            if polygon.contains(point):
                village_info = {
                    "province": record[4],
                    "district": record[6],
                    "sector": record[8],
                    "cell": record[10],
                    "village": record[12],
                }
                break

        if not village_info:
            return error_response("Point is not inside any village polygon", status_code=404)

        user = request.user
        person = getattr(user, "person", None)
        if not person:
            return error_response("No person record for the user", status_code=400)

        existing_resident = Resident.objects.filter(person=person, is_deleted=False).first()
        if existing_resident:
            return error_response(
                f"You are already a resident in {existing_resident.Village.village} village in {existing_resident.Village.sector} sector",
                status_code=409
            )

        Village, _ = Village.objects.get_or_create(
            province=village_info["province"],
            district=village_info["district"],
            sector=village_info["sector"],
            cell=village_info["cell"],
            village=village_info["village"],
            defaults={"leader": None}
        )

        resident = Resident.objects.create(
            person=person,
            Village=Village,
            added_by=user,
            status="PENDING"
        )

        if Village.leader:
            notify_village_leader_new_resident.delay(
                Village.leader.email,
                f"{person.first_name} {person.last_name}",
                Village.village,
                Village.get_full_address()
            )

        serializer = ResidentSerializer(resident)
        return success_response(
            serializer.data,
            "Join request submitted successfully. Waiting for leader approval.",
            status_code=201
        )

