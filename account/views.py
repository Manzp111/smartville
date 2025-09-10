# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from pytz import timezone as pytz_timezone

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from .serializers import (
    RegisterSerializer,
    OTPVerifySerializer,
    ResendOTPSerializer,
    UserListSerializer
)
from .models import User
from .tasks import send_verification_email_task
from .permisions import IsAdminUser
from .utils import generate_otp


@extend_schema(
    request=RegisterSerializer,
    responses={201: OpenApiExample(
        'Account Created',
        value={
            "success": True,
            "message": "Account created. Verify your email using the OTP.",
            "data": {
                "email": "user@example.com"
            }
        },
        summary="Account successfully created"
    )},
    examples=[
        OpenApiExample(
            'Register Example',
            value={
                "email": "gilbertnshimyimana11@gmail.com",
                "password": "Ng635188@",
                "confirm_password": "Ng635188@",
                "person": {
                    "first_name": "Gilbert",
                    "last_name": "Nshimyimana",

                }
            },
            request_only=True,  # this example is for request body
            summary="Example request payload for registration"
        )
    ],
    description="Create a new user account. Returns a message to verify email using OTP.",
    summary="Register to be a user of system"
)
class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": f"Account created. Verify email using OTP for {user.email}"
            }, status=status.HTTP_201_CREATED)
        
        # Return first error as consistent message
        first_error = next(iter(serializer.errors.values()))
        message = first_error[0] if isinstance(first_error, list) else str(first_error)
        return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# OTP Verify View
# -----------------------------
@extend_schema(
    request=OTPVerifySerializer,
    responses={
        200: OpenApiExample(
            'OTP Verified',
            value={"success": True, "message": "User successfully verified.", "data": {"email": "user@example.com"}},
            summary="OTP verification successful"
        ),
        400: OpenApiExample(
            'OTP Failed',
            value={"success": False, "message": "Invalid or expired OTP."},
            summary="OTP verification failed"
        )
    },

    examples=[
        OpenApiExample(
            'OTP Verify Example',
            value={
                "email": "gilbertnshimyimana11@gmail.com",
                "otp_code": "123456"

            },
            request_only=True,  
            summary="Example request payload for OTP verification"
        )
    ],
    description="Verify a user's email using OTP. Sets is_verified=True on success.",
    summary="Verify email"
)
class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        
        first_error = next(iter(serializer.errors.values()))
        message = first_error[0] if isinstance(first_error, list) else str(first_error)
        return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# Resend OTP View
# -----------------------------
@extend_schema(
    request=ResendOTPSerializer,
    responses={
        200: OpenApiExample(
            "OTP Sent",
            value={"success": True, "message": "A new OTP has been sent to your email.", "data": {"email": "user@example.com"}},
            summary="Successfully resent OTP"
        ),
        400: OpenApiExample(
            "Validation Error",
            value={"success": False, "message": "User is already verified or resend cooldown not passed."},
            summary="Cannot resend OTP"
        )
    },
    examples=[
        OpenApiExample(
            'Resend OTP Example',
            value={
                "email": "gilbertnshimyimana11@gmail",

            },
            
            summary="Example request payload for resending OTP"
        )
    ],

    description="Resend a verification OTP to a user's email",
    summary="Resend verification OTP"
)
class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        
        first_error = next(iter(serializer.errors.values()))
        message = first_error[0] if isinstance(first_error, list) else str(first_error)
        return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)





class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = UserPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_verified', 'is_active', 'person__location']
    search_fields = ['email', 'person__first_name', 'person__last_name']
    ordering_fields = ['email', 'created_at', 'role']

    # ---------------- LIST ----------------
    @extend_schema(
        parameters=[
            OpenApiParameter("role", description="Filter by role", required=False, type=str),
            OpenApiParameter("is_verified", description="Filter by verification status", required=False, type=bool),
            OpenApiParameter("is_active", description="Filter by active status", required=False, type=bool),
            OpenApiParameter("person__location", description="Filter by location ID", required=False, type=int),
            OpenApiParameter("search", description="Search by email or name", required=False, type=str),
            OpenApiParameter("ordering", description="Order by email, created_at, or role", required=False, type=str),
            OpenApiParameter("page", description="Page number for pagination", required=False, type=int),
            OpenApiParameter("page_size", description="Number of users per page", required=False, type=int),
        ],
        description="List all users with filtering, search, ordering, and pagination",
        examples=[
            OpenApiExample(
                "Users List Example",
                value={
                    "success": True,
                    "message": "Users retrieved successfully",
                    "data": [
                        {
                            "user_id": "d7b4c8e2-9f62-4f4e-a7b5-1234567890ab",
                            "email": "gilbertnshimyimana11@gmail.com",
                            "role": "resident",
                            "is_verified": True,
                            "is_active": True,
                            "person": {
                                "first_name": "Gilbert",
                                "last_name": "Nshimyimana",
                                "phone_number": "250788123456",
                                "location": {
                                    "province": "Kigali",
                                    "district": "Gasabo",
                                    "sector": "Kimihurura",
                                    "cell": "Gisozi",
                                    "village": "Village"
                                }
                            },
                            "created_at": "2025-09-10T08:00:00Z"
                        }
                    ]
                },
                response_only=True,
                summary="Example response for users list"
            )
        ],
        responses={200: UserListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Users retrieved successfully",
            "data": response.data
        })

    # ---------------- RETRIEVE ----------------
    @extend_schema(
        description="Retrieve a single user by ID",
        examples=[
            OpenApiExample(
                "User Retrieve Example",
                value={
                    "success": True,
                    "message": "User retrieved successfully",
                    "data": {
                        "user_id": "d7b4c8e2-9f62-4f4e-a7b5-1234567890ab",
                        "email": "gilbertnshimyimana11@gmail.com",
                        "role": "resident",
                        "is_verified": True,
                        "is_active": True,
                        "person": {
                            "first_name": "Gilbert",
                            "last_name": "Nshimyimana",
                            "phone_number": "250788123456",
                            "location": {
                                "province": "Kigali",
                                "district": "Gasabo",
                                "sector": "Kimihurura",
                                "cell": "Gisozi",
                                "village": "Village"
                            }
                        },
                        "created_at": "2025-09-10T08:00:00Z"
                    }
                },
                response_only=True,
                summary="Example response for retrieve user"
            )
        ],
        responses={200: UserListSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "User retrieved successfully",
            "data": response.data
        })

    # ---------------- DELETE ----------------
    @extend_schema(
        description="Delete a user by ID",
        examples=[
            OpenApiExample(
                "User Delete Example",
                value={"success": True, "message": "User deleted successfully"},
                response_only=True,
                summary="Example response for delete user"
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"success": True, "message": "User deleted successfully"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE ----------------
    @extend_schema(
        description="Update a user's details by ID",
        examples=[
            OpenApiExample(
                "User Update Example",
                value={"success": True, "message": "User updated successfully"},
                response_only=True,
                summary="Example response for update user"
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({"success": True, "message": "User updated successfully", "data": response.data})

    # ---------------- RESEND OTP ----------------
    @extend_schema(
        summary="Resend OTP to unverified user",
        description="Resends the verification OTP to the user's email. Only works for unverified users.",
        examples=[
            OpenApiExample(
                'OTP Resent Example',
                value={"success": True, "message": "OTP resent to user@example.com"},
                summary="OTP successfully resent",
            ),
            OpenApiExample(
                'Already Verified Example',
                value={"success": False, "message": "User is already verified."},
                summary="Cannot resend OTP to verified user",
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='resend-otp')
    def resend_otp(self, request, pk=None):
        user = self.get_object()
        if user.is_verified:
            return Response({"success": False, "message": "User is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp(user, purpose="verification")
        send_verification_email_task.delay(
            user.person.first_name,
            user.person.last_name,
            user.email,
            otp.code
        )
        return Response({"success": True, "message": f"OTP resent to {user.email}"}, status=status.HTTP_200_OK)
