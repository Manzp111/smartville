# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
# from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Resident, Village
from .serializers import ResidentSerializer, ResidentStatusSerializer
from account.permisions import IsAdminUser, IsLeaderOrAdmin, IsVerifiedUser
from .tasks import notify_village_leader_new_resident
from event.utils import success_response, error_response
from .mixins import VillageRolePermissionMixin
from django_filters.rest_framework import DjangoFilterBackend
from .response import errorss__response
from django.db import transaction
from django.utils import timezone
from .tasks import notify_village_leaders_of_migration

@extend_schema_view(
    list=extend_schema(
        summary="List all residents",
        request=ResidentSerializer,
        description="""Retrieve a paginated list of residents based on user permissions:
        - **Admins**: See all residents
        - **Leaders**: See residents in their assigned Village
        - **Regular Users**: See only their own resident record
        
        Supports filtering, searching, and ordering.""",

        responses={
            200: OpenApiResponse(response=ResidentSerializer(many=True), description="Residents retrieved successfully"),
            403: OpenApiResponse(description="Forbidden - User not authorized"),
            500: OpenApiResponse(description="Internal server error")
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific resident",
        description="Get detailed information about a single resident by ID. User must have permission to access this resident.",
        responses={
            200: OpenApiResponse(response=ResidentSerializer, description="Resident retrieved successfully"),
            403: OpenApiResponse(description="Forbidden - User not authorized to view this resident"),
            404: OpenApiResponse(description="Resident not found")
        }
    ),
    create=extend_schema(
        summary="add a new resident for admin and leader eg like children",
        description="""Create a new resident record. This endpoint is typically used by admins/leaders to register new residents.
        For users joining villages, use the join_village endpoint instead.""",
        request=ResidentSerializer,
        responses={
            201: OpenApiResponse(response=ResidentSerializer, description="Resident created successfully"),
            400: OpenApiResponse(description="Validation error - Invalid input data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to create residents")
        },
        examples=[
            OpenApiExample(
                "Resident Example",
                value={
                                        
                    "person": {
                        "first_name": "Gilbert",
                        "last_name": "Nshimyimana",
                        "national_id": None,
                        "phone_number": "0788730366",
                        "gender": "male",
                        "person_type": "resident"
                    }
}

                
            )
        ],
    ),
    update=extend_schema(  exclude=True  
    
    ),
    partial_update=extend_schema(
        summary="Partially update a resident",
        description="Partially update a resident record. User must have permission to modify this resident.",
        request=ResidentSerializer,
        responses={
            200: OpenApiResponse(response=ResidentSerializer, description="Resident partially updated successfully"),
            400: OpenApiResponse(description="Validation error - Invalid input data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to update this resident"),
            404: OpenApiResponse(description="Resident not found")
        }
    ),
    destroy=extend_schema(
        summary="Permanently delete a resident",
        description="""**WARNING**: Permanently delete a resident record from the database. 
        This action is irreversible. For safe deletion, use the soft_delete endpoint instead.
        Only available to admin users.""",
        responses={
            204: OpenApiResponse(description="Resident permanently deleted successfully"),
            403: OpenApiResponse(description="Forbidden - Only admin users can permanently delete"),
            404: OpenApiResponse(description="Resident not found")
        }
    )
)



class ResidentViewSet(VillageRolePermissionMixin,viewsets.ModelViewSet):
    """
    ViewSet for managing Resident records with role-based access control.
    
    Provides endpoints for creating, retrieving, updating, and deleting residents
    with appropriate permissions for different user roles.
    """
    queryset = Resident.objects.filter(is_deleted=False)
    serializer_class = ResidentSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    lookup_field = 'resident_id'
    filterset_fields = ["status","person__first_name","created_at"]
    search_fields = ["person__full_name"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Resident.objects.filter(is_deleted=False)
        elif user.role == "leader":
            return Resident.objects.filter(is_deleted=False, village__leader=user)
        else:
            return Resident.objects.filter(is_deleted=False, person=user.person)

# Resident/views.py
    @extend_schema(
        summary="Join a village community",
        description="""Allows verified users to join a specific village community by providing Village details.
        The system will find or create the Village and create a resident record with PENDING status.""",
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Join Request Example",
                summary="Example request to join a village",
                value={
                    "province": "Amajyaruguru",
                    "district": "Burera", 
                    "sector": "Kinyababa",
                    "cell": "Bugamba",
                    "village": "Kirwa"
                },
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(
                response=ResidentSerializer,
                description="Join request submitted successfully",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        summary="Successful join request",
                        value={
                            "status": "success",
                            "message": "Joined village successfully",
                            "data": {
                                "id": 1,
                                "status": "PENDING",
                                "person": {"id": 1, "full_name": "John Doe"},
                                "Village": {
                                    "village_id": "uuid-123",
                                    "province": "Amajyaruguru",
                                    "district": "Burera",
                                    "sector": "Kinyababa", 
                                    "cell": "Bugamba",
                                    "village": "Kirwa"
                                }
                            }
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(description="Validation error - Missing Village data"),
            409: OpenApiResponse(description="Conflict - Already a resident of this village")
        }
    )
    @action(detail=False, methods=["post"], permission_classes=[IsVerifiedUser])
    def join_village(self, request):
        user = request.user
        person = getattr(user, "person", None)
        
        if not person:
            return error_response("No person record for the user", status_code=400)
        
        # Extract Village data from request
        location_data = request.data
        required_fields = ['province', 'district', 'sector', 'cell', 'village']
        
        # Validate required fields
        missing_fields = [field for field in required_fields if not location_data.get(field)]
        if missing_fields:
            return error_response(
                f"Missing required Village fields: {', '.join(missing_fields)}",
                status_code=400
            )
        
        # Find or create the Village
        try:
            Village, created = Village.objects.get_or_create(
                province=location_data['province'],
                district=location_data['district'],
                sector=location_data['sector'],
                cell=location_data['cell'],
                village=location_data['village'],
                defaults={
                    # You can set default values if creating new Village
                    'leader': None  # or set a default leader if needed
                }
            )
        except Exception as e:
            return error_response(f"Error creating/finding Village: {str(e)}", status_code=400)
        
        # # Check if user is already a resident of this Village
        # if Resident.objects.filter(person=person, Village=Village, is_deleted=False).exists():
        #     return error_response("Already a resident of this village", status_code=409)
        
        # Create resident record with PENDING status
        existing_resident = Resident.objects.filter(person=person, is_deleted=False).first()
        if existing_resident:
           return error_response(
                     f"You are already a resident in {existing_resident.Village.village} village in {existing_resident.Village.sector} sector",
                      status_code=409
                )
        resident = Resident.objects.create(
            person=person,
            Village=Village,
            added_by=user,
            status='PENDING'  # Assuming you have a status field
        )
        
        # Notify village leader if one exists
        if Village.leader:
            notify_village_leader_new_resident.delay(
                Village.leader.email,
                f"{person.first_name} {person.last_name}",
                Village.village,
                Village.get_full_address()  # Assuming you have a method for this
            )
        
        serializer = self.get_serializer(resident)
        return success_response(
            serializer.data, 
            "Join request submitted successfully. Waiting for leader approval.", 
            status_code=201
        )
    @extend_schema(
        summary="Approve or reject resident status",
        description="""Allows village leaders and admins to approve or reject resident join requests.

        **Available Status Values:**
        - APPROVED: Resident is officially accepted into the village
        - REJECTED: Resident's join request is denied
        - PENDING: Initial status (default)

        **Permissions:** Village leaders (for their village) and admins only""",
        request=ResidentStatusSerializer,
        examples=[
            OpenApiExample(
                "Approve Request",
                summary="Example to approve residents",
                value={
                    "resident_ids": ["51f5fa35-037f-4616-b0ee-e14ce4ba7738"],
                    "status": "APPROVED"
                },
                request_only=True
            ),
            OpenApiExample(
                "Reject Request",
                summary="Example to reject a resident",
                value={"status": "REJECTED"},
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=ResidentSerializer,
                description="Status updated successfully",
            ),
            400: OpenApiResponse(description="Validation error - Invalid status value"),
            403: OpenApiResponse(description="Forbidden - User not authorized to update status"),
            404: OpenApiResponse(description="Resident not found")
        }
    )
    @action(detail=True, methods=["patch"], permission_classes=[IsLeaderOrAdmin], serializer_class=ResidentStatusSerializer)
    def update_status(self, request, *args, **kwargs):
        resident_ids = request.data.get("resident_ids")
        new_status = request.data.get("status")

        if not new_status:
            return error_response("status is required", 400)

        # Bulk update mode
        if resident_ids:
            queryset = Resident.objects.filter(resident_id__in=resident_ids, is_deleted=False)

            # queryset = Resident.objects.filter(id__in=resident_ids, is_deleted=False)
            if not queryset.exists():
                return error_response("No valid residents found to update", 404)
            queryset.update(status=new_status)
            serializer = ResidentSerializer(queryset, many=True)
            return success_response(serializer.data, f"Updated status of {queryset.count()} residents")

        # Single update mode
        resident = self.get_object()
        serializer = ResidentStatusSerializer(resident, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(ResidentSerializer(resident).data, "Resident status updated")


    # # --------------------- Soft Delete ---------------------
    # @extend_schema(
    #     summary="Soft delete a resident",
    #     description="""Marks a resident as deleted without permanently removing the record.
        
    #     **Features:**
    #     - Sets is_deleted flag to True
    #     - Record remains in database for audit purposes
    #     - Can be restored using the restore endpoint
    #     - Doesn't affect related person/Village records
        
    #     **Permissions:** Village leaders (for their village) and admins only""",
    #     responses={
    #         200: OpenApiResponse(
    #             description="Resident soft deleted successfully",
    #             examples=[
    #                 OpenApiExample(
    #                     "Soft Delete Success",
    #                     value={
    #                         "status": "success", 
    #                         "message": "Resident soft deleted successfully",
    #                         "data": None
    #                     }
    #                 )
    #             ]
    #         ),
    #         403: OpenApiResponse(description="Forbidden - User not authorized to delete"),
    #         404: OpenApiResponse(description="Resident not found")
    #     }
    # )
    # @action(detail=True, methods=["delete"], permission_classes=[IsLeaderOrAdmin])


    # def soft_delete(self, request, pk=None):
    #     resident = self.get_object()
    #     resident.soft_delete()
    #     return success_response(message="Resident soft deleted successfully")

    # --------------------- Restore Soft-Deleted Resident ---------------------
    @extend_schema(
        summary="Restore a soft-deleted resident",
        description="""Restores a previously soft-deleted resident record.
        
        **Features:**
        - Sets is_deleted flag back to False
        - Restores resident to active status
        - Maintains all original data and relationships
        
        **Permissions:** Village leaders (for their village) and admins only""",
        responses={
            200: OpenApiResponse(
                response=ResidentSerializer,
                description="Resident restored successfully",
                examples=[
                    OpenApiExample(
                        "Restore Success",
                        value={
                            "status": "success",
                            "message": "Resident restored successfully",
                            "data": {
                                "id": 1,
                                "status": "APPROVED",
                                "is_deleted": False,
                                "person": {"id": 1, "full_name": "John Doe"},
                                "Village": {"id": 123, "village": "Village A"}
                            }
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description="Forbidden - User not authorized to restore"),
            404: OpenApiResponse(description="Resident not found")
        }
    )
    @action(detail=True, methods=["post"], permission_classes=[IsLeaderOrAdmin])
    def restore(self, request, pk=None):
        resident = self.get_object()
        resident.restore()
        return success_response(self.get_serializer(resident).data, "Resident restored successfully")

  

    @extend_schema(
            summary="delete for admin"
            
            )  
    def destroy(self, request, *args, **kwargs):
        """Permanent delete - only for admin use"""
        return super().destroy(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(
                data=serializer.data, 
                message="Resident created successfully", 
                status_code=201
            )
        return errorss__response(
        
         errors=serializer.errors,
      status_code=status.HTTP_400_BAD_REQUEST
      )
    # resident/views.py


    @extend_schema(
        summary="Migrate resident to a new village",
        examples=[
            OpenApiExample(
                "Migration Example",
                value={
                    "province": "Amajyaruguru",
                    "district": "Burera",
                    "sector": "Kinyababa",
                    "cell": "Bugamba",
                    "village": "Kirwa"
                },
                summary="Example migration data"
            )
        ]
    )

    @action(detail=False, methods=["post"])





    def migrate_village(self, request):
        """
        Moves a resident to a new village. Soft deletes the old Resident record and creates a new one.
        Only allows migration if the new Village exists in the database.
        Notifies old and new village leaders asynchronously.
        """
        user = request.user
        person = getattr(user, "person", None)
        if not person:
            return error_response("No person record found for this user.", status_code=400)

        # Validate required Village fields
        location_data = request.data
        required_fields = ["province", "district", "sector", "cell", "village"]
        missing_fields = [f for f in required_fields if not location_data.get(f)]
        if missing_fields:
            return error_response(
                f"Missing required Village fields: {', '.join(missing_fields)}",
                status_code=400
            )

        # Match the Village exactly with existing DB records
        try:
            new_location = Village.objects.get(
                province=location_data["province"],
                district=location_data["district"],
                sector=location_data["sector"],
                cell=location_data["cell"],
                village=location_data["village"]
            )
        except Village.DoesNotExist:
            return error_response(
                "The specified village does not exist in the system. Please check the Village data.",
                status_code=404
            )

        try:
            with transaction.atomic():
                # Soft delete old resident if exists
                old_resident = Resident.objects.filter(person=person, is_deleted=False).first()
                old_location_id = None
                if old_resident:
                    old_resident.is_deleted = True
                    old_resident.deleted_at = timezone.now()
                    old_resident.save()
                    old_location_id = old_resident.Village.village_id

                # Create new resident record
                new_resident = Resident.objects.create(
                    person=person,
                    Village=new_location,
                    added_by=user,
                    status="PENDING"
                )

                # Send background notifications to leaders
                notify_village_leaders_of_migration.delay(
                    resident_name=f"{person.first_name} {person.last_name}",
                    old_location_id=old_location_id,
                    new_location_id=new_location.village_id
                )

        except Exception as e:
            return error_response(f"Error migrating resident: {str(e)}", status_code=500)

        serializer = ResidentSerializer(new_resident)
        return success_response(
            serializer.data,
            "Resident migrated successfully to new village.",
            status_code=201
        )
