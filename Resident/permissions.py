# account/permissions.py

from rest_framework import permissions
from .utils import get_resident_location

class IsInResidentVillage(permissions.BasePermission):
    """
    Only allows access to objects in the resident's village.
    """

    def has_object_permission(self, request, view, obj):
        location = get_resident_location(request.user)
        if not location:
            return False
        return hasattr(obj, 'location') and obj.location == location
