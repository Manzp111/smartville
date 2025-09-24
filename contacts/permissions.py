# contacts/permissions.py
from rest_framework import permissions


class IsLeaderOrAdmin(permissions.BasePermission):
    """
    Custom permission: Only leaders or admins can create/edit contacts.
    """

    def has_permission(self, request, view):
        # Safe methods (GET, HEAD, OPTIONS) are allowed for anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For create/update/delete, check if user is leader or admin
        return request.user.is_authenticated and (
            request.user.role in ["leader", "admin"]
        )
