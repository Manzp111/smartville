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
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from django.shortcuts import get_object_or_404
from django.db import transaction

from .serializers import LeaderSerializer, PromoteToLeaderSerializer, UpdateLeaderSerializer
from account.models import User, Person
from Village.models import Village
from .permissions import IsSystemAdmin


class LeaderViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
    ViewSet for managing village leaders.
    System admins can perform all actions except retrieving leaders (allowed for any authenticated user).
    """
    # queryset = User.objects.filter(role='leader', is_deleted=False)
    queryset  = User.objects.filter(led_villages__isnull=False)

    serializer_class = LeaderSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]  # Allow anyone to view leaders
        else:
            permission_classes = [IsSystemAdmin]  # Only system admins for other actions
        return [permission() for permission in permission_classes]

    # -------------------------------
    # List all leaders (GET /leaders/)
    # -------------------------------
    @extend_schema(
        summary="List all village leaders",
        description="Retrieve a list of all village leaders. This endpoint is accessible to any user.",

        parameters=[
            OpenApiParameter(
                name='page',
                description='Page number for pagination (default: 1)',
                required=False,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name='limit',
                description='Number of results per page (default: 10)',
                required=False,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name='sortBy',
                description='Field to sort by (e.g. "created_at", "first_name")',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='sortOrder',
                description='Sort order: "asc" or "desc"',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='search',
                description='Search leaders by first name, last name, phone number, or village name and id',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='province',
                description='Filter leaders by province',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='district',
                description='Filter leaders by district',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='sector',
                description='Filter leaders by sector',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='cell',
                description='Filter leaders by cell',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='village_id',
                description='Filter leaders by village ID',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='includeDeleted',
                description='If true, include deleted leaders',
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name='deletedOnly',
                description='If true, return only deleted leaders',
                required=False,
                type=OpenApiTypes.BOOL,
            ),
        ]
    ,
        responses={
            200: OpenApiResponse(
                response=LeaderSerializer(many=True),
                description="List of leaders retrieved successfully"
            )
        },
        examples=[
            OpenApiExample(
                "Success Response Example",
                value={
                    "success": True,
                    "message": "Leaders retrieved successfully",
                    "count": 2,
                    "data": [
                        {
                            "user_id": "a1b2c3d4-5678-9012-3456-7890abcdef12",
                            "first_name": "John",
                            "last_name": "Doe",
                            "phone_number": "250781234567",
                            "email": "john.doe@example.com",
                            "role": "leader",
                            "is_active": True,
                            "village": "Kigali, Nyarugenge, Nyamirambo, Rwezamenyo"
                        },
                        {
                            "user_id": "b2c3d4e5-6789-0123-4567-890abcdef123",
                            "first_name": "Jane",
                            "last_name": "Smith",
                            "phone_number": "250782345678",
                            "email": "jane.smith@example.com",
                            "role": "leader",
                            "is_active": True,
                            "village": "Kigali, Gasabo, Kimihurura, Gishushu"
                        }
                    ]
                },
                response_only=True,
                status_codes=['200']
            )
        ]
    )
    def list(self, request):
            """List leaders with pagination, filters, and search"""
            leaders = self.get_queryset()

            # --------------------
            # Filtering parameters
            # --------------------
            province = request.query_params.get("province")
            district = request.query_params.get("district")
            sector = request.query_params.get("sector")
            cell = request.query_params.get("cell")
            village_id = request.query_params.get("village_id")
            include_deleted = request.query_params.get("includeDeleted") == "true"
            deleted_only = request.query_params.get("deletedOnly") == "true"

            if not include_deleted and not deleted_only:
                leaders = leaders.filter(is_deleted=False)
            if deleted_only:
                leaders = leaders.filter(is_deleted=True)

            if province:
                leaders = leaders.filter(led_villages__province__iexact=province)
            if district:
                leaders = leaders.filter(led_villages__district__iexact=district)
            if sector:
                leaders = leaders.filter(led_villages__sector__iexact=sector)
            if cell:
                leaders = leaders.filter(led_villages__cell__iexact=cell)
            if village_id:
                leaders = leaders.filter(led_villages__village_id=village_id)

            # --------------------
            # Search
            # --------------------
            search = request.query_params.get("search")
            if search:
                leaders = leaders.filter(
                    Q(person__first_name__icontains=search) |
                    Q(person__last_name__icontains=search) |
                    Q(person__national_id__icontains=search) |
                    Q(phone_number__icontains=search) |
                    Q(led_villages__village__icontains=search)
                )

            # --------------------
            # Sorting
            # --------------------
            sort_by = request.query_params.get("sortBy", "created_at")
            sort_order = request.query_params.get("sortOrder", "desc")
            if sort_order == "desc":
                sort_by = f"-{sort_by}"
            leaders = leaders.order_by(sort_by)

            # --------------------
            # Pagination
            # --------------------
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 10))
            total = leaders.count()
            total_pages = (total + limit - 1) // limit

            start = (page - 1) * limit
            end = start + limit
            leaders = leaders[start:end]

            # --------------------
            # Response
            # --------------------
            serializer = self.get_serializer(leaders, many=True)
            return Response({
                "success": True,
                "message": "Leaders retrieved successfully",
                "data": serializer.data,
                "meta": {
                        "page": page,                 # current page
                        "limit": limit,               # items per page
                        "total": total,               # total records
                        "total_pages": total_pages,   # total number of pages
                        "has_next": page < total_pages,
                        "has_prev": page > 1
                    },
            }, status=status.HTTP_200_OK)

    # -------------------------------
    # Retrieve a specific leader (GET /leaders/{id}/)
    # -------------------------------
    @extend_schema(
        summary="Retrieve a specific leader",
        description="Get detailed information about a specific village leader by ID. This endpoint is accessible to any user.",
        responses={
            200: OpenApiResponse(
                response=LeaderSerializer,
                description="Leader details retrieved successfully"
            ),
            404: OpenApiResponse(
                description="Leader not found"
            )
        },
        examples=[
            OpenApiExample(
                "Success Response Example",
                value={
                    "status": "success",
                    "message": "Leader retrieved successfully",
                    "data": {
                        "user_id": "a1b2c3d4-5678-9012-3456-7890abcdef12",
                        "first_name": "John",
                        "last_name": "Doe",
                        "phone_number": "250781234567",
                        "email": "john.doe@example.com",
                        "role": "leader",
                        "is_active": True,
                        "village": "Kigali, Nyarugenge, Nyamirambo, Rwezamenyo",
                        "created_at": "2023-10-15T08:30:45Z",
                        "updated_at": "2023-11-20T14:22:18Z"
                    }
                },
                response_only=True,
                status_codes=['200']
            )
        ]
    )
    def retrieve(self, request, pk=None):
        """Get details of a specific leader"""
        leader = self.get_object()
        serializer = self.get_serializer(leader)
        
        return Response({
            "status": "success",
            "message": "Leader retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # -------------------------------
    # Disable PUT method (not allowed)
    # -------------------------------
    def update(self, request, *args, **kwargs):
        return Response({
            "status": "error",
            "message": "PUT method is not allowed. Use PATCH for partial updates."
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # -------------------------------
    # Partial update leader (PATCH /leaders/{id}/)
    # -------------------------------
    @extend_schema(
        summary="Partially update a leader",
        description="System admin can partially update a leader's information. Only provided fields will be updated.",
        request=UpdateLeaderSerializer,
        responses={
            200: OpenApiResponse(
                response=LeaderSerializer,
                description="Leader updated successfully"
            ),
            400: OpenApiResponse(
                description="Bad request - validation error"
            ),
            404: OpenApiResponse(
                description="Leader not found"
            )
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone_number": "250781234567",
                    "email": "john.doe@example.com",
                    "is_active": True
                },
                request_only=True,
            ),
            OpenApiExample(
                "Success Response Example",
                value={
                    "status": "success",
                    "message": "Leader updated successfully",
                    "data": {
                        "user_id": "a1b2c3d4-5678-9012-3456-7890abcdef12",
                        "first_name": "John",
                        "last_name": "Doe",
                        "phone_number": "250781234567",
                        "email": "john.doe@example.com",
                        "role": "leader",
                        "is_active": True,
                        "village": "Kigali, Nyarugenge, Nyamirambo, Rwezamenyo"
                    }
                },
                response_only=True,
                status_codes=['200']
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a leader's information"""
        leader = self.get_object()
        serializer = UpdateLeaderSerializer(leader, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Leader updated successfully",
                    "data": LeaderSerializer(leader).data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # Delete a leader (soft delete) (DELETE /leaders/{id}/)
    # -------------------------------
    @extend_schema(
        summary="Delete a leader",
        description="System admin can soft delete a leader. The leader will be marked as deleted but not removed from the database.",
        responses={
            200: OpenApiResponse(
                description="Leader soft deleted successfully"
            ),
            404: OpenApiResponse(
                description="Leader not found"
            )
        },
        examples=[
            OpenApiExample(
                "Success Response Example",
                value={
                    "status": "success",
                    "message": "Leader soft deleted successfully",
                    "data": {
                        "user_id": "a1b2c3d4-5678-9012-3456-7890abcdef12",
                        "first_name": "John",
                        "last_name": "Doe",
                        "deleted_at": "2023-12-01T10:30:45Z"
                    }
                },
                response_only=True,
                status_codes=['200']
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        """Soft delete a leader"""
        leader = self.get_object()
        leader.soft_delete()
        
        return Response({
            "status": "success",
            "message": "Leader soft deleted successfully",
            "data": {
                "user_id": str(leader.user_id),
                "first_name": leader.person.first_name if leader.person else None,
                "last_name": leader.person.last_name if leader.person else None,
                "deleted_at": leader.deleted_at
            }
        }, status=status.HTTP_200_OK)

    # -------------------------------
    # Promote resident to leader (POST /leaders/promote/)
    # -------------------------------
    @extend_schema(
        summary="Promote a resident to leader",
        description="System admin assigns a resident to a village and promotes them to leader.",
        request=PromoteToLeaderSerializer,
        responses={
            200: OpenApiResponse(
                response=LeaderSerializer,
                description="Resident successfully promoted to leader"
            ),
            400: OpenApiResponse(
                description="Bad request - validation error or user already a leader"
            ),
            404: OpenApiResponse(
                description="User or village not found"
            )
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "user_id": "a1b2c3d4-5678-9012-3456-7890abcdef12",
                    "village_id": "v1w2x3y4-5678-9012-3456-abcdef123456"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Success Response Example",
                value={
                    "status": "success",
                    "message": "Resident promoted to leader successfully",
                    "data": {
                        "user_id": "a1b2c3d4-5678-9012-3456-7890abcdef12",
                        "first_name": "John",
                        "last_name": "Doe",
                        "phone_number": "250781234567",
                        "email": "john.doe@example.com",
                        "role": "leader",
                        "village": "Kigali, Nyarugenge, Nyamirambo, Rwezamenyo"
                    }
                },
                response_only=True,
                status_codes=['200']
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='promote')
    def promote_resident(self, request):
        serializer = PromoteToLeaderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                leader = serializer.save()
                
                return Response({
                    "status": "success",
                    "message": "Resident promoted to leader successfully",
                    "data": LeaderSerializer(leader).data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "PUT method is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # -------------------------------
    # Remove leader from village (demote to resident) (DELETE /leaders/{id}/remove/)
    # -------------------------------
    @extend_schema(
        summary="Remove leader from village",
        description="System admin can remove a leader from their village, reverting their role to resident.",
        responses={
            200: OpenApiResponse(
                description="Leader removed successfully"
            ),
            404: OpenApiResponse(
                description="Leader not found"
            )
        },
        examples=[
            OpenApiExample(
                "Success Response Example",
                value={
                    "status": "success",
                    "message": "Leader removed successfully and reverted to resident",
                    "data": {
                        "user_id": "a1b2c3d4-5678-9012-3456-7890abcdef12",
                        "first_name": "John",
                        "last_name": "Doe",
                        "phone_number": "250781234567",
                        "role": "resident",
                        "previous_village": "Kigali, Nyarugenge, Nyamirambo, Rwezamenyo"
                    }
                },
                response_only=True,
                status_codes=['200']
            )
        ]
    )
    @action(detail=True, methods=['delete'], url_path='remove')
    def remove_leader(self, request, pk=None):
        leader = self.get_object()
        
        try:
            with transaction.atomic():
                # Get village info before removal for response
                village_info = None
                try:
                    village = Village.objects.get(leader=leader)
                    village_info = str(village)
                except Village.DoesNotExist:
                    pass
                
                # Update leader role to resident
                leader.role = 'resident'
                leader.save()
                
                # Remove from village
                Village.objects.filter(leader=leader).update(leader=None)
                
                return Response({
                    "status": "success", 
                    "message": "Leader removed successfully and reverted to resident",
                    "data": {
                        "user_id": str(leader.user_id),
                        "first_name": leader.person.first_name if leader.person else None,
                        "last_name": leader.person.last_name if leader.person else None,
                        "phone_number": leader.phone_number,
                        "role": leader.role,
                        "previous_village": village_info
                    }
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)