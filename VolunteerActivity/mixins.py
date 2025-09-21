from rest_framework import permissions
from Resident.models import Resident


class IsApprovedResident(permissions.BasePermission):
    """Check if user is an approved resident"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        try:
            resident = Resident.objects.get(
                person=request.user.person, 
                is_deleted=False,
                status='APPROVED'
            )
            return True
        except Resident.DoesNotExist:
            return False


class CanManageEvent(permissions.BasePermission):
    """Check if user can manage specific event"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.role == 'admin':
            return True
            
        if user.role == 'leader' and hasattr(obj, 'village'):
            return obj.village.leader == user
            
        if hasattr(obj, 'organizer'):
            return obj.organizer == user
            
        # For participation objects
        if hasattr(obj, 'event'):
            return obj.event.can_user_manage(user)
            
        return False


class IsEventOrganizer(permissions.BasePermission):
    """Check if user is the event organizer"""
    def has_object_permission(self, request, view, obj):
        return obj.organizer == request.user


class IsVillageLeader(permissions.BasePermission):
    """Check if user is leader of the event's village"""
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'leader' and obj.village.leader == request.user