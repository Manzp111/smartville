# event/permissions.py
from rest_framework.permissions import BasePermission

class EventAccessPermission(BasePermission):
    """
    Admin: full access
    Leader: access events in villages they lead
    Resident: access only their own events
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "admin":
            return True
        if user.role == "leader":
            return obj.village.leader == user
        if user.role == "resident":
            return obj.organizer == user
        return False
