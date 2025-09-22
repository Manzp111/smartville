from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import Resident
from .resident_serializers import ResidentDetailSerializer
from account.models import User


# 1. Get by Resident ID
@extend_schema(
    summary="Get Resident by Resident ID",
    description="Retrieve full resident details (including person, village, and added_by) using the resident_id.",
    responses={
        200: OpenApiResponse(
            response=ResidentDetailSerializer,
            description="Resident details fetched successfully."
        ),
        404: OpenApiResponse(description="Resident not found.")
    },
    # parameters=[
    #     OpenApiParameter(
    #         name="resident_id",
    #         description="UUID of the resident",
    #         required=True,
    #         type={"type": "string", "format": "uuid"}
    #     )
    # ]
)
class ResidentDetailView(generics.RetrieveAPIView):
    queryset = Resident.objects.all()
    serializer_class = ResidentDetailSerializer
    lookup_field = "resident_id"

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "success": True,
                "message": "Resident details fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Resident.DoesNotExist:
            return Response({
                "success": False,
                "message": "Resident not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)


# 2. Get by User ID
@extend_schema(
    summary="Get Resident by User ID",
    description="Retrieve full resident details (including person, village, and added_by) using the user's user_id.",
    responses={
        200: OpenApiResponse(
            response=ResidentDetailSerializer,
            description="Resident details fetched successfully."
        ),
        404: OpenApiResponse(description="Resident not found.")
    },
    # parameters=[
    #     OpenApiParameter(
    #         name="user_id",
    #         description="UUID of the user",
    #         required=True,
    #         type={"type": "string", "format": "uuid"}
    #     )
    # ]
)
class ResidentByUserView(generics.RetrieveAPIView):
    serializer_class = ResidentDetailSerializer

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(user_id=user_id)
            resident = Resident.objects.get(person=user.person, is_deleted=False)
            serializer = self.get_serializer(resident)
            return Response({
                "success": True,
                "message": "Resident details fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except (User.DoesNotExist, Resident.DoesNotExist):
            return Response({
                "success": False,
                "message": "Resident not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
