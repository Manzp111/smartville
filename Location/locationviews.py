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
                description="Village location found successfully",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "success": True,
                            "message": "Location found successfully",
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
                            "message": "Validation failed",
                            "errors": {
                                "latitude": ["This field is required."],
                                "longitude": ["This field is required."]
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Location Not Found",
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
                            "message": "Failed to process location data",
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
                message="Validation failed",
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
                    message="Location data not available",
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
                    message="Location found successfully",
                    status_code=status.HTTP_200_OK
                )
            else:
                return error_response(
                    message="Point is not inside any village polygon",
                    status_code=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            return error_response(
                message="Failed to process location data",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


