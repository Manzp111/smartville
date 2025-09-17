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


# Village/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.db.models import Q

from .models import Village
from .serializers import LocationSerializer
from event.utils import success_response, error_response


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing locations with hierarchical filtering.
    """
    queryset = Village.objects.all()
    serializer_class = LocationSerializer

    @extend_schema(
        summary="Get hierarchical Village data chose from district",
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
        """Get hierarchical Village data with unique values"""
        try:
            province = request.query_params.get('province')
            district = request.query_params.get('district')
            sector = request.query_params.get('sector')
            cell = request.query_params.get('cell')

            # Return unique provinces
            if not any([province, district, sector, cell]):
                provinces = Village.objects.values_list('province', flat=True).distinct()
                return success_response(
                    data={"provinces": sorted(provinces)},
                    message="Provinces retrieved successfully"
                )

            # Return districts for a province
            if province and not district and not sector and not cell:
                districts = Village.objects.filter(province=province)\
                    .values_list('district', flat=True).distinct()
                return success_response(
                    data={"districts": sorted(districts)},
                    message=f"Districts in {province} retrieved successfully"
                )

            # Return sectors for a district
            if province and district and not sector and not cell:
                sectors = Village.objects.filter(province=province, district=district)\
                    .values_list('sector', flat=True).distinct()
                return success_response(
                    data={"sectors": sorted(sectors)},
                    message=f"Sectors in {district}, {province} retrieved successfully"
                )

            # Return cells for a sector
            if province and district and sector and not cell:
                cells = Village.objects.filter(province=province, district=district, sector=sector)\
                    .values_list('cell', flat=True).distinct()
                return success_response(
                    data={"cells": sorted(cells)},
                    message=f"Cells in {sector}, {district} retrieved successfully"
                )

            # Return villages for a cell
            if province and district and sector and cell:
                villages = Village.objects.filter(
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
                message="Failed to retrieve Village data", 
                errors=str(e), 
                status_code=400
            )



########## managing leaders
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample
from account.models import User
from .models import Village
from .serializers import LeaderSerializer, PromoteToLeaderSerializer, UpdateLeaderSerializer

# -------------------------------
# Custom permission: System Admin only
# -------------------------------


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import LeaderSerializer, PromoteToLeaderSerializer, UpdateLeaderSerializer
from account.models import User
from Village.models import Village
from .permissions import IsSystemAdmin


class LeaderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing village leaders.
    Only system admins can perform these actions.
    """
    queryset = User.objects.filter(role='leader')
    serializer_class = LeaderSerializer
    permission_classes = [IsSystemAdmin]

    # -------------------------------
    # Promote resident to leader
    # -------------------------------
    @extend_schema(
        summary="Promote a resident to leader",
        description="System admin assigns a resident to a village and promotes them to leader.",
        request=PromoteToLeaderSerializer,
        responses={200: LeaderSerializer},
        examples=[
            OpenApiExample(
                "Promote Resident Example",
                value={
                    "user_id": "a1b2c3d4-5678-9012-3456-7890abcdef12",
                    "village_id": "v1w2x3y4-5678-9012-3456-abcdef123456"
                },
                request_only=True,
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='promote')
    def promote_resident(self, request):
        serializer = PromoteToLeaderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leader = serializer.save()
        return Response({
            "status": "resident promoted to leader",
            "leader": LeaderSerializer(leader).data
        })

    # -------------------------------
    # Update leader info
    # -------------------------------
    @extend_schema(
        summary="Update leader info",
        description="System admin can update leader's details (name, phone, email, active status) using PATCH.",
        request=UpdateLeaderSerializer,
        responses={200: LeaderSerializer},
        examples=[
            OpenApiExample(
                "Update Leader Info Example",
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone_number": "250781234567",
                    "email": "john.doe@example.com",
                    "is_active": True
                },
                request_only=True,
            )
        ]
    )
    @action(detail=True, methods=['patch'], url_path='update-info')
    def update_info(self, request, pk=None):
        leader = self.get_object()
        serializer = UpdateLeaderSerializer(leader, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "leader info updated",
            "leader": LeaderSerializer(leader).data
        })

    # -------------------------------
    # Remove leader from village (demote to resident)
    # -------------------------------
    @extend_schema(
        summary="Remove leader from village",
        description="System admin can remove a leader from their village, reverting their role to resident.",
        responses={200: OpenApiExample("Leader removed", value={"status": "leader removed"})}
    )
    @action(detail=True, methods=['delete'], url_path='remove')
    def remove_leader(self, request, pk=None):
        leader = self.get_object()
        leader.role = 'resident'
        leader.save()
        # Remove from village
        Village.objects.filter(leader=leader).update(leader=None)
        return Response({"status": "leader removed"}, status=status.HTTP_200_OK)
