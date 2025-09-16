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
from event.utils import success_response, error_response  # Import the utils
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from event.utils import success_response,error_response

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


# -----------------------------
# Register View
# -----------------------------
@extend_schema(
    request=RegisterSerializer,
    responses={
        201: OpenApiExample(
            'Account Created',
            value={
                "success": True,
                "message": "Account created. Verify your email using the OTP.",
                "data": {
                    "email": "gilbertnshimyimana11@gmail.com.com"
                }
            },
            summary="Account successfully created"
        ),
        400: OpenApiExample(
            'Validation Error',
            value={
                "success": False,
                "message": "Email already exists",
                "errors": {
                    "email": ["user with this email already exists."]
                }
            },
            summary="Registration validation failed"
        )
    },
    examples=[
        OpenApiExample(
            'Register Example',
            value={
                "phone_number": "0788730366",
                "password": "Ng112233@",
                "confirm_password": "Ng112233@",
                "person": {
                    "first_name": "Gilbert",
                    "last_name": "Nshimyimana",                    
                    "national_id": 123456789,
                    "gender": "male",
                    
                }

            },
            request_only=True,
            summary="Example request payload for registration using phone number"
        )
    ],

    description="Create a new user account with phonenumber used in login ",
    summary="Register to be a user of system"
)
class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(
                data={"phone_number": user.phone_number},
                message=f"Account created",
                status_code=status.HTTP_201_CREATED
            )

        
       
        return error_response(errors=serializer.errors)


# -----------------------------
# OTP Verify View
# -----------------------------
@extend_schema(
    request=OTPVerifySerializer,
    responses={
        200: OpenApiExample(
            'OTP Verified',
            value={
                "success": True, 
                "message": "User successfully verified.", 
                "data": {
                    "email": "user@example.com",
                    "is_verified": True
                }
            },
            summary="OTP verification successful"
        ),
        400: OpenApiExample(
            'OTP Failed',
            value={
                "success": False, 
                "message": "Invalid or expired OTP.",
                "errors": {
                    "otp_code": ["Invalid OTP code."]
                }
            },
            summary="OTP verification failed"
        )
    },
    examples=[
        OpenApiExample(
            'OTP Verify Example',
            value={
                "email": "gilbertnshimyimana130@gmail.com",
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
            return success_response(
                data=result,
                message="User successfully verified.",
                status_code=status.HTTP_200_OK
            )
        
        return error_response(
            message="OTP verification failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


# -----------------------------
# Resend OTP View
# -----------------------------
@extend_schema(
    request=ResendOTPSerializer,
    responses={
        200: OpenApiExample(
            "OTP Sent",
            value={
                "success": True, 
                "message": "A new OTP has been sent to your email.", 
                "data": {
                    "email": "user@example.com",
                    "cooldown_remaining": 60
                }
            },
            summary="Successfully resent OTP"
        ),
        400: OpenApiExample(
            "Validation Error",
            value={
                "success": False, 
                "message": "User is already verified or resend cooldown not passed.",
                "errors": {
                    "email": ["User is already verified."]
                }
            },
            summary="Cannot resend OTP"
        )
    },
    examples=[
        OpenApiExample(
            'Resend OTP Example',
            value={
                "email": "gilbertnshimyimana11@gmail.com"
            },
            request_only=True,
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
            return success_response(
                data=result,
                message="A new OTP has been sent to your email.",
                status_code=status.HTTP_200_OK
            )
        
        return error_response(            
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


# -----------------------------
# Admin User Management ViewSet
# -----------------------------
class UserPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 50


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = UserPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_verified', 'is_active']
    search_fields = ['email', 'person__first_name', 'person__last_name']
    ordering_fields = ['email', 'created_at', 'role']

    # ---------------- LIST ----------------
    @extend_schema(
        # parameters=[
        #     OpenApiParameter("role", description="Filter by role", required=False, type=str),
        #     OpenApiParameter("is_verified", description="Filter by verification status", required=False, type=bool),
        #     OpenApiParameter("is_active", description="Filter by active status", required=False, type=bool),
        #     OpenApiParameter("search", description="Search by email or name", required=False, type=str),
        #     OpenApiParameter("ordering", description="Order by email, created_at, or role", required=False, type=str),
        #     OpenApiParameter("page", description="Page number for pagination", required=False, type=int),
        #     OpenApiParameter("page_size", description="Number of users per page", required=False, type=int),
        # ],
        description="List all users with filtering, search, ordering, and pagination",
        summary="List users for admin only",
        examples=[
            OpenApiExample(
                "Users List Example",
                value={
                    "success": True,
                    "message": "Users retrieved successfully",
                    "data": {
                        "count": 150,
                        "next": "https://api.example.com/users/?page=2",
                        "previous": None,
                        "results": [
                            {
                                "user_id": "d7b4c8e2-9f62-4f4e-a7b5-1234567890ab",
                                "email": "gilbertnshimyimana130@gmail.com",
                                "role": "resident",
                                "is_verified": True,
                                "is_active": True,
                                "person": {
                                    "first_name": "Gilbert",
                                    "last_name": "Nshimyimana",
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
                    }
                },
                response_only=True,
                summary="Example response for users list"
            )
        ],
        responses={200: UserListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        return success_response(

            data=response.data,
            message="Users retrieved successfully"
        )
    
    # ---------------- CREATE ----------------
    @extend_schema(
        summary="Create a new user",
        description="Admin can create a new user with associated person and location info.",
        request=UserListSerializer,
        examples=[
            OpenApiExample(
                'Create User Example',
                value={
                    "email": "gilbertnshimyimana4@gmail.com",
                    "password": "Ng112233@",
                    "confirm_password": "Ng112233@",
                    "role": "resident",
                    "person": {
                        "first_name": "manzp",
                        "last_name": "prience",
                        "location": {
                            "province": "Kigali",
                            "district": "Gasabo",
                            "sector": "Kimihurura",
                            "cell": "Gisozi",
                            "village": "Village"
                        }
                    }
                },
                request_only=True,
                summary="Example payload to create a user"
            )
        ],
        responses={
            201: OpenApiExample(
                'User Created',
                value={
                    "success": True,
                    "message": "User created successfully",
                    "data": {
                        "id": "d7b4c8e2-9f62-4f4e-a7b5-1234567890ab",
                        "email": "gilbertnshimyimana4@gmail.com.com",
                        "role": "resident",
                        "is_verified": False,
                        "is_active": True,
                        "person": {
                            "first_name": "manzp",
                            "last_name": "prience",
                            "location": {
                                "province": "Kigali",
                                "district": "Gasabo",
                                "sector": "Kimihurura",
                                "cell": "Musezero",
                                "village": "Amajyambere"
                            }
                        },
                        "created_at": "2025-09-10T08:00:00Z"
                    }
                },
                response_only=True,
                summary="Example response after creating a user"
            )
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(
                data=UserListSerializer(user).data,
                message="User created successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return error_response(
            message="User creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # ---------------- RETRIEVE ----------------
    @extend_schema(
        description="Retrieve a single user by ID",
        summary="Retrieve user details for admin only",
        examples=[
            OpenApiExample(
                "User Retrieve Example",
                value={
                    "success": True,
                    "message": "User retrieved successfully",
                    "data": {
                        "user_id": "d7b4c8e2-9f62-4f4e-a7b5-1234567890ab",
                        "email": "gilbertnshimyimana4@gmail.com",
                        "role": "resident",
                        "is_verified": True,
                        "is_active": True,
                        "person": {
                            "first_name": "Gilbert",
                            "last_name": "Nshimyimana",
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
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="User with given id retrieved successfully"
        )

    # ---------------- DELETE ----------------
    @extend_schema(
        description="Delete a user by ID",
        summary="Delete user for admin only",
        examples=[
            OpenApiExample(
                "User Delete Example",
                value={
                    "success": True, 
                    "message": "User deleted successfully"
                },
                response_only=True,
                summary="Example response for delete user"
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(
            message="User deleted successfully"
        )

    # ---------------- UPDATE ----------------
   

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT", detail="Updating events is disabled.")
    
    
    # ---------------- PARTIAL UPDATE ----------------
    @extend_schema(
        summary="Update user partially",
        description="Admin can partially update user fields (PATCH request).",
        request=UserListSerializer,
        examples=[
            OpenApiExample(
                'Partial Update User Example',
                value={
                    "role": "leader",
                    "is_active": False
                },
                request_only=True,
                summary="Example payload to partially update a user"
            )
        ],
        responses={
            200: OpenApiExample(
                'User Updated',
                value={
                    "success": True,
                    "message": "User updated successfully",
                    "data": {
                        "id": "d7b4c8e2-9f62-4f4e-a7b5-1234567890ab",
                        "email": "gilbertnshimyimana130@gmail.com",
                        "role": "leader",
                        "is_verified": True,
                        "is_active": False,
                        "person": {
                            "first_name": "Gilbert",
                            "last_name": "Nshimyimana",
                            "location": {
                                "province": "Kigali",
                                "district": "Gasabo",
                                "sector": "Kimihurura",
                                "cell": "Gisozi",
                                "village": "Village"
                            }
                        },
                        "updated_at": "2025-09-10T12:00:00Z"
                    }
                },
                response_only=True,
                summary="Example response after partially updating a user"
            )
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    # ---------------- RESEND OTP ----------------
    @extend_schema(
        summary="Resend verification OTP",
        description=(
            "Resends the email verification OTP to the user's registered email address. "
            "This endpoint works only for users who have not verified their email yet."
        ),
        parameters=[
            OpenApiParameter(
                "pk", description="ID of the user to resend OTP", required=True, type=str
            )
        ],
        examples=[
            OpenApiExample(
                'OTP Resent Example',
                value={
                    "success": True,
                    "message": "OTP resent to gilbertnshimyimana130@gmail.com",
                    "data": {
                        "email": "gilbertnshimyimana130@gmail.com",
                        "cooldown_remaining": 60
                    }
                },
                summary="OTP successfully resent",
                response_only=True
            ),
            OpenApiExample(
                'Already Verified Example',
                value={
                    "success": False,
                    "message": "User is already verified.",
                    "errors": {
                        "user": ["User is already verified."]
                    }
                },
                summary="Cannot resend OTP to verified user",
                response_only=True
            )
        ],
        responses={
            200: OpenApiExample(
                'OTP Resent Response',
                value={
                    "success": True,
                    "message": "OTP resent to gilbertnshimyimana130@gmail.com"
                },
                response_only=True
            ),
            400: OpenApiExample(
                'Already Verified Response',
                value={
                    "success": False,
                    "message": "User is already verified."
                },
                response_only=True
            )
        }
    )
    @action(detail=True, methods=['post'], url_path='resend-otp')
    def resend_otp(self, request, pk=None):
        user = self.get_object()
        if user.is_verified:
            return error_response(
                message="User is already verified.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        otp = generate_otp(user, purpose="verification")
        send_verification_email_task.delay(
            user.person.first_name,
            user.person.last_name,
            user.email,
            otp.code
        )
        
        return success_response(
            data={"email": user.email, "cooldown_remaining": 60},
            message=f"OTP resent to {user.email}"
        )