# account/jwt_views.py
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import User
from event.utils import error_response,success_response
from .error_responses import errorss__response
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError
from .jwt_serializers import CustomTokenObtainPairSerializer

# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)

#         # Check if user is verified
#         if not self.user.is_verified:
#             raise serializers.ValidationError({
                
#                 "message": "Email not verified"
#             })

#         return {
#             "status": "success",
#             "message": "Login successful",
#             "data": {
#                 "access": data["access"],
#                 "refresh": data["refresh"],
#                 "user": {
#                     "id": self.user.user_id,
#                     "email": self.user.email,
#                     "role": self.user.role
#                 }
#             }
#         }

@extend_schema(
    request=CustomTokenObtainPairSerializer,
    summary="User Login we used JWT authentication",
    examples=[
        OpenApiExample(
            "Login Example",
            value={
                "email": "gilbertnshimyimana130@gmail.com",
                "password": "Ng112233@"
            },
            request_only=True,
            summary="Example login payload"
        ),
        OpenApiExample(
            "Login Success Response",
            value={
                "status": "success",
                "message": "Login successful",
                "data": {
                    "access": "<access_token>",
                    "refresh": "<refresh_token>",
                    "user": {
                        "id": 1,
                        "email": "gilbertnshimyimana130@gmail.com",
                        "role": "resident"
                    }
                }
            },
            response_only=True,
            summary="Example successful login response"
        ),
        OpenApiExample(
            "Email Not Verified",
            value={
                "status": "error",
                "message": "Email not verified"
            },
            response_only=True,
            summary="Response if email is not verified"
        )
    ],
)



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        return success_response(
            data=serializer.validated_data,
            message="Login successful"
        )
    except ValidationError as e:
        return errorss__response(errors=e.detail)
# -----------------------------
# Custom Token Refresh
# -----------------------------
@extend_schema(
    request=TokenRefreshSerializer,
    examples=[
        OpenApiExample(
            "Refresh Token Request",
            value={"refresh": "<refresh_token>"},
            request_only=True,
            summary="Refresh token payload"
        ),
        OpenApiExample(
            "Refresh Token Success",
            value={
                "status": "success",
                "message": "Token refreshed successfully",
                "data": {"access": "<new_access_token>"}
            },
            response_only=True,
            summary="Successful token refresh response"
        ),
        OpenApiExample(
            "Invalid Refresh Token",
            value={
                "status": "error",
                "message": "Invalid refresh token"
            },
            response_only=True,
            summary="Response if refresh token is invalid"
        )
    ]
)


        
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                "status": "success",
                "message": "Token refreshed successfully",
                "data": serializer.validated_data
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                "status": "error",
                "message": "Invalid refresh token"
            }, status=status.HTTP_400_BAD_REQUEST)
