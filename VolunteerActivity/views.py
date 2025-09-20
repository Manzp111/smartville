# volunteering/views.py

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from .models import VolunteeringEvent
from .serializers import VolunteeringEventSerializer, VolunteeringEventCreateSerializer
from Village.models import Village
from Resident.models import Resident
# -------------------------
# Role-based Permission
# -------------------------
class IsOrganizerOrLeader:
    """
    Role-based access for Volunteering Events:
    - resident: can see their own events
    - leader: can see events in their villages
    - admin: full access
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["resident", "leader", "admin"]

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "resident":
            return obj.organizer == user
        elif user.role == "leader":
            return obj.village.leader == user
        return True  # admin

# -------------------------
# Custom Pagination
# -------------------------
class VolunteeringEventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "message": "Volunteering events fetched successfully",
            "data": data,
            "meta": {
                "page": self.page.number,
                "limit": self.page.paginator.per_page,
                "total": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "has_next": self.page.has_next(),
                "has_prev": self.page.has_previous(),
                "next_page": self.get_next_link(),
                "previous_page": self.get_previous_link()
            }
        })

# -------------------------
# Volunteering Event ViewSet
# -------------------------
class VolunteeringEventViewSet(viewsets.ModelViewSet):
    queryset = VolunteeringEvent.objects.all()
    serializer_class = VolunteeringEventSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrLeader]
    pagination_class = VolunteeringEventPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        # Automatically set the organizer to the current user
        serializer.save(organizer=self.request.user)

    # --------------------------
    # List Volunteering Events
    # --------------------------
    @extend_schema(
        summary="List Volunteering Events",
        description=(
            "Fetch paginated volunteering events.\n"
            "- Residents see their own events.\n"
            "- Leaders see events in their villages.\n"
            "- Admins see all events.\n\n"
            "Supports search by `title` or `description`.\n"
            "Response includes pagination metadata and next/prev page links."
        ),
        responses={
            200: OpenApiResponse(
                description="Paginated volunteering event list",
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={
                            "success": True,
                            "message": "Volunteering events fetched successfully",
                            "data": [
                                {
                                    "volunteer_id": "uuid1",
                                    "title": "Community Clean-up",
                                    "description": "Cleaning the local park",
                                    "date": "2025-10-01",
                                    "start_time": "08:00:00",
                                    "end_time": "12:00:00",
                                    "capacity": 20,
                                    "village": "uuid_village",
                                    "organizer": "uuid_user",
                                    "status": "DRAFT",
                                    "skills_required": ["Teamwork", "Physical Fitness"],
                                    "category": "Community & Social",
                                    "created_at": "2025-09-20T09:00:00Z",
                                    "updated_at": "2025-09-20T09:00:00Z",
                                    "approved_at": None
                                }
                            ],
                            "meta": {
                                "page": 1,
                                "limit": 10,
                                "total": 45,
                                "total_pages": 5,
                                "has_next": True,
                                "has_prev": False
                            }
                        }
                    )
                ]
            )
        }
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.queryset

        if user.role == "resident":
            queryset = queryset.filter(organizer=user)
        elif user.role == "leader":
            queryset = queryset.filter(village__leader=user)
        
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # --------------------------
    # Retrieve a Volunteering Event
    # --------------------------
    @extend_schema(
        summary="Retrieve a Volunteering Event",
        description="Fetch details of a single volunteering event.",
        responses={
            200: OpenApiResponse(
                description="Event details",
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={
                            "success": True,
                            "message": "Event details fetched successfully",
                            "data": {
                                "volunteer_id": "uuid",
                                "title": "Community Clean-up",
                                "description": "Cleaning the local park",
                                "date": "2025-10-01",
                                "start_time": "08:00:00",
                                "end_time": "12:00:00",
                                "capacity": 20,
                                "village": "uuid",
                                "organizer": "uuid",
                                "status": "DRAFT",
                                "skills_required": ["Teamwork", "Physical Fitness"],
                                "category": "Community & Social",
                                "created_at": "2025-09-20T09:00:00Z",
                                "updated_at": "2025-09-20T09:00:00Z",
                                "approved_at": None
                            }
                        }
                    )
                ]
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        event = self.get_object()
        self.check_object_permissions(request, event)
        serializer = self.get_serializer(event)
        return Response({"success": True, "message": "Event details fetched successfully", "data": serializer.data})

    # --------------------------
    # Create a Volunteering Event
    # --------------------------
    @extend_schema(
        summary="Create a Volunteering Event",
        description="Create a volunteering event. Organizer and village are auto-assigned based on logged-in user.",
        request=VolunteeringEventCreateSerializer,
        examples=[
            OpenApiExample(
                name="create volunteer event",
                value={
                    
                        "title": "Community Clean-up",
                        "description": "Cleaning the local park and planting trees",
                        "date": "2025-10-01",
                        "start_time": "08:00:00",
                        "end_time": "12:00:00",
                        "capacity": 20,
                        "skills_required": ["Teamwork", "Physical Fitness"],
                        "category": "Community & Social"


                }
            )
        ],
        responses={
            201: OpenApiResponse(
                description="Event created successfully",
                examples=[
                    OpenApiExample(
                        "Response Example",
                        value={
                            "success": True,
                            "message": "Volunteering event created successfully",
                            "data": {
                                "volunteer_id": "uuid",
                                "title": "Community Clean-up",
                                "description": "Cleaning the local park",
                                "date": "2025-10-01",
                                "start_time": "08:00:00",
                                "end_time": "12:00:00",
                                "capacity": 20,
                                "village": "uuid",
                                "organizer": "uuid",
                                "status": "DRAFT",
                                "skills_required": ["Teamwork", "Physical Fitness"],
                                "created_at": "2025-09-20T09:00:00Z",
                                "updated_at": "2025-09-20T09:00:00Z",
                                "approved_at": None
                            }
                        }
                    )
                ]
            )
        }
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Assign village automatically based on role
        if request.user.role == "resident":
            resident_obj = request.user.person.residencies.first()
            if not resident_obj:
                return Response({"success": False, "message": "Resident profile not found"}, status=400)
            data["village"] = resident_obj.village.pk
        elif request.user.role == "leader":
            village_obj = request.user.led_villages.first()
            if village_obj:
                data["village"] = village_obj.pk
        else:
            return Response(
                {   "success":False,
                   "message":"gilbert didn't handle admin creation please use resident account or leader account",
                   }


                )

        # Create serializer (accept PKs)
        serializer = VolunteeringEventCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Save event and set organizer
        volunteer_event = serializer.save(organizer=request.user)

        # Use full serializer for response (nested village + organizer)
        output_serializer = VolunteeringEventSerializer(volunteer_event)

        return Response(
            {
                "success": True,
                "message": "Volunteering event created successfully",
                "data": output_serializer.data,
            },
            status=201
        )


    # --------------------------
    # Update a Volunteering Event
    # --------------------------
    @extend_schema(
        summary="Update a Volunteering Event",
        description="Update a volunteering event. Only organizers, leaders, or admin can update.",
        request=VolunteeringEventSerializer,
        responses={
            200: OpenApiResponse(
                description="Event updated successfully",
                examples=[
                    OpenApiExample(
                        "Response Example",
                        value={
                            "success": True,
                            "message": "Volunteering event updated successfully",
                            "data": {
                                "volunteer_id": "uuid",
                                "title": "Community Clean-up Updated",
                                "description": "Updated description",
                                "date": "2025-10-01",
                                "start_time": "08:00:00",
                                "end_time": "12:00:00",
                                "capacity": 25,
                                "village": "uuid",
                                "organizer": "uuid",
                                "status": "APPROVED",
                                "skills_required": ["Teamwork", "Physical Fitness"],
                                "created_at": "2025-09-20T09:00:00Z",
                                "updated_at": "2025-09-21T09:00:00Z",
                                "approved_at": "2025-09-21T10:00:00Z"
                            }
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Volunteering event updated successfully", "data": serializer.data})

    # --------------------------
    # Delete a Volunteering Event
    # --------------------------
    @extend_schema(
        summary="Delete a Volunteering Event",
        description="Delete a volunteering event. Only organizers, leaders, or admin can delete.",
        responses={
            204: OpenApiResponse(description="Event deleted successfully")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"success": True, "message": "Volunteering event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# -------------------------
# Village Event ViewSet
# -------------------------
class VillageEventViewSet(viewsets.ViewSet):
    """
    ViewSet to list volunteering events of a specific village with role-based access.
    """

    @extend_schema(
        summary="List Volunteering Events for a Village enter vllage id ",
        description=(
            "Returns all volunteering events for a given village. "
            "Residents see only events they organized. "
            "Leaders see all events in villages they lead. "
            "Admin sees all events. Paginated response with metadata."
        ),
        responses={
            200: OpenApiResponse(
                response=VolunteeringEventSerializer(many=True),
                description="Successful Response",
                examples=[
                    OpenApiExample(
                        "Sample Response",
                        value={
                            "status": "success",
                            "message": "Events for village Kabuga",
                            "count": 2,
                            "data": [
                                {
                                    "volunteer_id": "uuid1",
                                    "title": "Tree Planting",
                                    "description": "Community tree planting",
                                    "date": "2025-09-25",
                                    "start_time": "09:00",
                                    "end_time": "12:00",
                                    "capacity": 20,
                                    "village": "uuid_village",
                                    "organizer": "uuid_user",
                                    "status": "APPROVED",
                                    "skills_required": ["Planting", "Coordination"],
                                    "category": "Environmental & Sustainability",
                                    "created_at": "2025-09-20T09:00:00Z",
                                    "updated_at": "2025-09-20T09:00:00Z",
                                    "approved_at": "2025-09-20T10:00:00Z"
                                }
                            ],
                            "meta": {
                                "page": 1,
                                "limit": 10,
                                "total": 2,
                                "total_pages": 1,
                                "has_next": False,
                                "has_prev": False
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description="Village not found")
        }
    )
    def list(self, request, village_id=None):
        """List volunteering events of a specific village based on user role"""
        try:
            village = Village.objects.get(village_id=village_id)
        except Village.DoesNotExist:
            return Response({"status": "error", "message": "Village not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        queryset = VolunteeringEvent.objects.filter(village=village)

        # Role-based filtering
        # if user.role == "resident":
        #     queryset = queryset.filter(organizer=user)
        # elif user.role == "leader":
        #     if village.leader != user:
        #         return Response({"status": "error", "message": "You do not have access to this village"}, status=status.HTTP_403_FORBIDDEN)

        # queryset = queryset.order_by("-date", "-start_time")

        # Pagination
        paginator = VolunteeringEventPagination()
        paginator.page_size = request.query_params.get("page_size", 10)
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = VolunteeringEventSerializer(result_page, many=True)

        meta = {
            "page": paginator.page.number,
            "limit": paginator.page.paginator.per_page,
            "total": paginator.page.paginator.count,
            "total_pages": paginator.page.paginator.num_pages,
            "has_next": paginator.page.has_next(),
            "has_prev": paginator.page.has_previous()
        }

        return Response({
            "status": "success",
            "message": f"Events for village {village.village}",
            "count": len(serializer.data),
            "data": serializer.data,
            "meta": meta
        })


# ###################################
# class VillageEventViewSet(viewsets.ViewSet):
#     """
#     ViewSet to list volunteering events of a specific village with role-based access.
#     """

#     @extend_schema(
#         summary="List Volunteering Events for a Village (Role-Aware)",
#         description=(
#             "Returns all volunteering events for a given village. "
#             "Residents see only events they organized. "
#             "Leaders see all events in villages they lead. "
#             "Admin sees all events. Paginated response with metadata."
#         ),
#         responses={
#             200: OpenApiResponse(
#                 response=VolunteeringEventSerializer(many=True),
#                 description="Successful Response",
#                 examples=[
#                     OpenApiExample(
#                         "Sample Response",
#                         value={
#                             "status": "success",
#                             "message": "Events for village Kabuga",
#                             "count": 2,
#                             "data": [
#                                 {
#                                     "volunteer_id": "uuid1",
#                                     "title": "Tree Planting",
#                                     "description": "Community tree planting",
#                                     "date": "2025-09-25",
#                                     "start_time": "09:00",
#                                     "end_time": "12:00",
#                                     "capacity": 20,
#                                     "village": "uuid_village",
#                                     "organizer": "uuid_user",
#                                     "status": "APPROVED",
#                                     "skills_required": ["Planting", "Coordination"],
#                                     "category": "Environmental & Sustainability",
#                                     "created_at": "2025-09-20T09:00:00Z",
#                                     "updated_at": "2025-09-20T09:00:00Z",
#                                     "approved_at": "2025-09-20T10:00:00Z"
#                                 }
#                             ],
#                             "meta": {
#                                 "page": 1,
#                                 "limit": 10,
#                                 "total": 2,
#                                 "total_pages": 1,
#                                 "has_next": False,
#                                 "has_prev": False
#                             }
#                         }
#                     )
#                 ]
#             ),
#             404: OpenApiResponse(description="Village not found")
#         }
#     )
#     def list(self, request, village_id=None):
#         """List volunteering events of a specific village based on user role"""
#         try:
#             village = Village.objects.get(village_id=village_id)
#         except Village.DoesNotExist:
#             return Response({"status": "error", "message": "Village not found"}, status=status.HTTP_404_NOT_FOUND)

#         user = request.user
#         queryset = VolunteeringEvent.objects.filter(village=village)

#         # Role-based filtering
#         if user.role == "resident":
#             queryset = queryset.filter(organizer=user)
#         elif user.role == "leader":
#             # Leaders see events in villages they lead
#             if not village in user.led_villages.all():
#                 return Response({"status": "error", "message": "You do not have access to this village"}, status=status.HTTP_403_FORBIDDEN)
#             # queryset already filtered by village
#         # Admin sees all

#         queryset = queryset.order_by("-date", "-start_time")

#         # Pagination
#         paginator = PageNumberPagination()
#         paginator.page_size = request.query_params.get("page_size", 10)
#         result_page = paginator.paginate_queryset(queryset, request)

#         serializer = VolunteeringEventSerializer(result_page, many=True)

#         meta = {
#             "page": paginator.page.number,
#             "limit": paginator.page.paginator.per_page,
#             "total": paginator.page.paginator.count,
#             "total_pages": paginator.page.paginator.num_pages,
#             "has_next": paginator.page.has_next(),
#             "has_prev": paginator.page.has_previous()
#         }

#         return Response({
#             "status": "success",
#             "message": f"Events for village {village.village}",
#             "count": len(serializer.data),
#             "data": serializer.data,
#             "meta": meta
#         })
