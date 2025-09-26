from rest_framework import viewsets, status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .models import Complaint
from .serializers import ComplaintSerializer
from .utils import success_response, error_response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import MethodNotAllowed, NotAuthenticated
from Village.models import Village
from .mixins import ComplaintRolePermissionMixin
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response


TAG = ["Complaints"]

class ComplaintViewSet(viewsets.ModelViewSet, ComplaintRolePermissionMixin):
    queryset = Complaint.objects.all().order_by('-date_submitted')
    serializer_class = ComplaintSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'location', 'date_submitted']
    ordering = ['-date_submitted']

    # def get_permissions(self):
    #     if self.action in ['update', 'partial_update', 'destroy', 'list']:
    #         return [permissions.IsAdminUser()]
    #     return [permissions.IsAuthenticated()]

    def get_permissions(self):
        if self.action == "retrieve":
            return [AllowAny()]   # 👈 public access only for retrieve
        return [IsAuthenticated()]

    @extend_schema(
        summary="Create complaint",
        description="Automatically assigns the complainant and village based on the logged-in user.",
        request=ComplaintSerializer,
        responses={
            201: OpenApiResponse(response=ComplaintSerializer, description="Complaint created successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                name="create complaint",
                value={
                    "description": "No water in the taps for 3 days.",
                    "status": "pending",
                    "is_anonymous": False,
                }
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Authentication required to submit a complaint.")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            from Resident.models import Resident
            try:
                resident = Resident.objects.get(person__user=user, is_deleted=False)
                village = resident.village
            except Resident.DoesNotExist:
                return error_response(
                    errors="You must be assigned to a village to submit a complaint.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(complainant=user, location=village) #""", location=village"""
            return success_response(
                data=serializer.data,
                message="Complaint created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Retrieve complaints according to user role",
        description="Admins see all, leaders see their village, residents see their own.",
        responses={200: ComplaintSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True) if page is not None else self.get_serializer(queryset, many=True)
        data = serializer.data
        if page is not None:
            return self.get_paginated_response(data)
        return success_response(data=data, message="Complaints retrieved successfully")

    # @extend_schema(exclude=True)
    # def update(self, request, *args, **kwargs):
    #     raise MethodNotAllowed("PUT", detail="Updating complaints is disabled.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
            "success":True,
            "message":"Complaint deleted successfully",
        
        },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        request=ComplaintSerializer,
        summary="Partially update complaint (status only for leader/admin)",
        responses={
            200: OpenApiResponse(response=ComplaintSerializer, description="Complaint updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Forbidden - no permission"),
            404: OpenApiResponse(description="Complaint not found")
        },
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().partial_update(request, *args, **kwargs)