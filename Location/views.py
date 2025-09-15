from django.shortcuts import render
import shapefile
from shapely.geometry import Point, shape
#postgresql://:@dpg-d31jvrjuibrs73928oc0-a.oregon-postgres.render.com/

def locate_point(request):
    result = None

    if request.method == "POST":
        latitude = float(request.POST.get("latitude"))
        longitude = float(request.POST.get("longitude"))

        # Load shapefile
        # sf = shapefile.Reader(r"C:\Users\highe\OneDrive\Desktop\Capstone Project\Village_level_boundary\RWA_adm5.shp")
        sf = shapefile.Reader(r"C:\Users\highe\OneDrive\Desktop\Capstone Project\Village level boundary\RWA_adm5.shp")

        point = Point(longitude, latitude)

        for record, shp in zip(sf.records(), sf.shapes()):
            polygon = shape(shp.__geo_interface__)
            if polygon.contains(point):
                result = {
                    "province": record[4],
                    "district": record[6],
                    "sector": record[8],
                    "cell": record[10],
                    "village": record[12],
                }
                break

    return render(request, "home/home.html", {"result": result})


# Location/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.db.models import Q

from .models import Location
from .serializers import LocationSerializer
from event.utils import success_response, error_response


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing locations with hierarchical filtering.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @extend_schema(
        summary="Get hierarchical location data chose from district",
        description="""Retrieve locations in a hierarchical manner. 
        - Get all provinces
        - Filter districts by province
        - Filter sectors by district
        - Filter cells by sector
        - Filter villages by cell""",
        parameters=[
            OpenApiParameter(name='province', description='Filter districts by province', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='district', description='Filter sectors by district', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='sector', description='Filter cells by sector', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='cell', description='Filter villages by cell', required=False, type=OpenApiTypes.STR),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        }
    )
    @action(detail=False, methods=['get'])
    def hierarchical(self, request):
        """Get hierarchical location data with unique values"""
        try:
            province = request.query_params.get('province')
            district = request.query_params.get('district')
            sector = request.query_params.get('sector')
            cell = request.query_params.get('cell')

            # Return unique provinces
            if not any([province, district, sector, cell]):
                provinces = Location.objects.values_list('province', flat=True).distinct()
                return success_response(
                    data={"provinces": sorted(provinces)},
                    message="Provinces retrieved successfully"
                )

            # Return districts for a province
            if province and not district and not sector and not cell:
                districts = Location.objects.filter(province=province)\
                    .values_list('district', flat=True).distinct()
                return success_response(
                    data={"districts": sorted(districts)},
                    message=f"Districts in {province} retrieved successfully"
                )

            # Return sectors for a district
            if province and district and not sector and not cell:
                sectors = Location.objects.filter(province=province, district=district)\
                    .values_list('sector', flat=True).distinct()
                return success_response(
                    data={"sectors": sorted(sectors)},
                    message=f"Sectors in {district}, {province} retrieved successfully"
                )

            # Return cells for a sector
            if province and district and sector and not cell:
                cells = Location.objects.filter(province=province, district=district, sector=sector)\
                    .values_list('cell', flat=True).distinct()
                return success_response(
                    data={"cells": sorted(cells)},
                    message=f"Cells in {sector}, {district} retrieved successfully"
                )

            # Return villages for a cell
            if province and district and sector and cell:
                villages = Location.objects.filter(
                    province=province, 
                    district=district, 
                    sector=sector, 
                    cell=cell
                ).values('village_id', 'village')
                return success_response(
                    
                    data={"villages": list(villages)},
                    message=f"Villages in {cell}, {sector} retrieved successfully"
                )

            return error_response(
                message="Invalid filter combination",
                errors="Provide filters in hierarchical order: province → district → sector → cell",
                status_code=400
            )

        except Exception as e:
            return error_response(
                message="Failed to retrieve location data", 
                errors=str(e), 
                status_code=400
            )
