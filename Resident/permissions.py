# account/permissions.py

from rest_framework import permissions
from .utils import get_resident_location

class IsInResidentVillage(permissions.BasePermission):
    """
    Only allows access to objects in the resident's village.
    """

    def has_object_permission(self, request, view, obj):
        Village = get_resident_location(request.user)
        if not Village:
            return False
        return hasattr(obj, 'Village') and obj.Village == Village
