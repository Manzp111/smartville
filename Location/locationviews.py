from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import LocatePointSerializer
import shapefile
from shapely.geometry import Point, shape
import os

class LocatePointAPIView(APIView):

    @extend_schema(
        request=LocatePointSerializer,
        responses={
            200: LocatePointSerializer,  # or you can define a response serializer
            404: OpenApiExample(
                'Not Found',
                value={"message": "Point is not inside any village polygon"},
                response_only=True
            )
        },
        description="Send latitude and longitude to find the corresponding village.",
        summary="Locate a village by coordinates",
        examples=[
            OpenApiExample(
                "Sample Point",
                value={"latitude": -1.3782236, "longitude": 29.8094301},
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = LocatePointSerializer(data=request.data)
        if serializer.is_valid():
            latitude = serializer.validated_data["latitude"]
            longitude = serializer.validated_data["longitude"]

            # Adjust the path to your shapefile
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            shp_path = os.path.join(BASE_DIR, "Village level boundary", "RWA_adm5.shp")

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
                return Response(village_info)
            else:
                return Response({"message": "Point is not inside any village polygon"}, status=404)
        else:
            return Response(serializer.errors, status=400)
