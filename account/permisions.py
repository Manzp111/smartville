from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    message = "Access denied: Admins  verified email."
    def has_permission(self, request, view):
        return bool(
            request.user
            
            and request.user.is_authenticated
            and request.user.is_verified
            and request.user.role == 'admin'
            and request.user.is_verified
        )

class IsLeaderOrAdmin(permissions.BasePermission):
    message = "Access denied: village only and must be verified."
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ['leader', 'admin']
            and request.user.is_verified
        )

class IsVerifiedUser(permissions.BasePermission):
    message = "Email not verified"
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )
