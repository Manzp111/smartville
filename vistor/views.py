# visitor/views.py
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from .models import Visitor
from .serializers import VisitorSerializer
from account.models import User

# -------------------------
# Role-based Permission
# -------------------------

TAG = ["Visitor"]

class IsResidentOrLeader:
    """
    Role-based access for Visitor:
    - resident: can create and see their own visitors
    - leader: can see visitors of their village
    - admin: full access
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["resident", "leader", "admin"]

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "resident":
            return obj.resident.person == user.person
        elif user.role == "leader":
            return obj.village.leader == user
        return True  # admin


# -------------------------
# Custom Pagination
# -------------------------
class VisitorPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "message": "Visitors fetched successfully",
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
# Visitor ViewSet
# -------------------------
class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.all().order_by('-created_at')
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated, IsResidentOrLeader]
    pagination_class = VisitorPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['resident__resident_id', 'village__village_id']

    # # Disable PUT/PATCH completely
    # def get_extra_actions(self):
    #     return []

    # def get_allowed_methods(self):
    #     allowed = super().get_allowed_methods()
    #     return [method for method in allowed if method not in ['PUT']]

    # --------------------------
    # List Visitors
    # --------------------------
    @extend_schema(
        summary="List Visitors",
        description=(
            "Fetch paginated visitors.\n"
            "- Residents see their own visitors.\n"
            "- Leaders see visitors of their village.\n"
            "- Admins see all visitors.\n\n"
            "Supports search by `resident_id` or `village_id`.\n"
            "Response includes pagination metadata and next/prev page links."
        ),
        responses={
            200: OpenApiResponse(
                description="Paginated visitor list",
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={
                            "success": True,
                            "message": "Visitors fetched successfully",
                            "data": [
                                {
                                    "visitor_id": "e7f1d9c2-3c0e-4d1f-a6f5-9b7a12345678",
                                    "resident": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
                                    "resident_name": "John",
                                    "name": "Jane Doe",
                                    "phone_number": "250788123456",
                                    "id_number": "123456789",
                                    "purpose_of_visit": "Meeting",
                                    "expected_duration": "2 hours",
                                    "vehicle_info": "Toyota Corolla",
                                    "date": "2025-09-20",
                                    "time_in": "09:30:00",
                                    "time_out": "11:30:00",
                                    "village": "b1c2d3e4-5678-90ab-cdef-0987654321ab",
                                    "village_name": "Village A, Cell X, Sector Y, District Z, Province P",
                                    "created_at": "2025-09-20T08:00:00Z",
                                    "updated_at": "2025-09-20T08:05:00Z"
                                }
                            ],
                            "meta": {
                                "page": 1,
                                "limit": 10,
                                "total": 45,
                                "total_pages": 5,
                                "has_next": True,
                                "has_prev": False,
                                "next_page": "http://api.example.com/visitors/?page=2",
                                "previous_page": None
                            }
                        }
                    )
                ]
            )
        }
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        if user.role == "resident":
            queryset = self.queryset.filter(resident__person=user.person)
        elif user.role == "leader":
            queryset = self.queryset.filter(village__leader=user)
        else:
            queryset = self.queryset

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "message": "Visitors fetched successfully", "data": serializer.data})

    # --------------------------
    # Retrieve Visitor
    # --------------------------
    @extend_schema(
        summary="Retrieve Visitor",
        description="Fetch details of a single visitor. Role-based access enforced.",
        responses={
            200: OpenApiResponse(
                description="Visitor details",
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={
                            "success": True,
                            "message": "Visitor details fetched successfully",
                            "data": {
                                "visitor_id": "e7f1d9c2-3c0e-4d1f-a6f5-9b7a12345678",
                                "resident": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
                                "resident_name": "John",
                                "name": "Jane Doe",
                                "phone_number": "250788123456",
                                "id_number": "123456789",
                                "purpose_of_visit": "Meeting",
                                "expected_duration": "2 hours",
                                "vehicle_info": "Toyota Corolla",
                                "date": "2025-09-20",
                                "time_in": "09:30:00",
                                "time_out": "11:30:00",
                                "village": "b1c2d3e4-5678-90ab-cdef-0987654321ab",
                                "village_name": "Village A, Cell X, Sector Y, District Z, Province P",
                                "created_at": "2025-09-20T08:00:00Z",
                                "updated_at": "2025-09-20T08:05:00Z"
                            }
                        }
                    )
                ]
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        visitor = self.get_object()
        self.check_object_permissions(request, visitor)
        serializer = self.get_serializer(visitor)
        return Response({"success": True, "message": "Visitor details fetched successfully", "data": serializer.data})

    # --------------------------
    # Create Visitor
    # --------------------------
    @extend_schema(
        summary="Create Visitor",
        description="Create a visitor. Resident and village are auto-assigned based on logged-in user.",
        request=VisitorSerializer,
        examples=[
            OpenApiExample(
                "create resident",
                value={
                                        "name": "Furaha justine",
                    "phone_number": "0788730366",
                    "id_number": "123456789",
                    "purpose_of_visit": "Dating",
                    "expected_duration": "2 hours",
                    "vehicle_info": "Toyota Corolla",
                    "date": "2025-09-20",
                    "time_in": "09:30:00",
                    "time_out": "11:30:00"


                },
            )
        ],
        responses={
            201: OpenApiResponse(
                description="Visitor created successfully",
                examples=[
                    OpenApiExample(
                        "Request Example",
                        value={
                            "name": "Jane Doe",
                            "phone_number": "0788123456",
                            "id_number": "123456789",
                            "purpose_of_visit": "Meeting",
                            "expected_duration": "2 hours",
                            "vehicle_info": "Toyota Corolla",
                            "date": "2025-09-20",
                            "time_in": "09:30:00",
                            "time_out": "11:30:00"
                        }
                    ),
                    OpenApiExample(
                        "Response Example",
                        value={
                            "success": True,
                            "message": "Visitor created successfully",
                            "data": {
                                "visitor_id": "e7f1d9c2-3c0e-4d1f-a6f5-9b7a12345678",
                                "resident": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
                                "resident_name": "John",
                                "name": "Jane Doe",
                                "phone_number": "250788123456",
                                "id_number": "123456789",
                                "purpose_of_visit": "Meeting",
                                "expected_duration": "2 hours",
                                "vehicle_info": "Toyota Corolla",
                                "date": "2025-09-20",
                                "time_in": "09:30:00",
                                "time_out": "11:30:00",
                                "village": "b1c2d3e4-5678-90ab-cdef-0987654321ab",
                                "village_name": "Village A, Cell X, Sector Y, District Z, Province P",
                                "created_at": "2025-09-20T08:00:00Z",
                                "updated_at": "2025-09-20T08:05:00Z"
                            }
                        }
                    )
                ]
            )
        }
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        resident_obj = None

        # Assign resident and village based on role
        if request.user.role == "resident" and hasattr(request.user, "resident_set"):
            resident_obj = request.user.resident_set.first()
            data["resident"] = resident_obj.resident_id
            data["village"] = resident_obj.village.village_id
        elif request.user.role == "leader":
            village_obj = request.user.led_villages.first()
            if village_obj:
                data["village"] = village_obj.village_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Save with actual resident object if available
        visitor = serializer.save(resident=resident_obj) if resident_obj else serializer.save()

        output_serializer = self.get_serializer(visitor)
        return Response(
            {"success": True, "message": "Visitor created successfully", "data": output_serializer.data},
            status=status.HTTP_201_CREATED
        )

        # return Response({"success": True, "message": "Visitor created successfully", "data": output_serializer.data}, status=status.HTTP_201_CREATED)

    # --------------------------
    # Delete Visitor
    # --------------------------
    @extend_schema(
        summary="Delete Visitor",
        description="Delete a visitor. Only allowed for residents (own visitor), village leaders (same village), or admin.",
        responses={
            204: OpenApiResponse(
                description="Visitor deleted successfully",
                examples=[OpenApiExample(
                    "Response Example",
                    value={"success": True, "message": "Visitor deleted successfully"}
                )]
            )
        }
    )
    def destroy(self, request, *args, **kwargs):
        visitor = self.get_object()
        self.check_object_permissions(request, visitor)
        visitor.delete()
        return Response({"success": True, "message": "Visitor deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
