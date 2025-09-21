# event/mixins.py
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed, NotAuthenticated
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from Resident.utils import get_resident_location

class EventRolePermissionMixin:
    """
    Handles Event access based on user roles:
    - Admin: full access
    - Leader: access restricted to their village
    - Resident: access only to events they organized
    - Anonymous: read-only access to individual events by ID
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # For retrieve action, allow any user (handled by get_object)
        if self.action == 'retrieve':
            return qs

        # Anonymous users cannot access list/create/update/delete
        if not user.is_authenticated:
            raise NotAuthenticated("You must be logged in to access this resource.")

        if user.role == "admin":
            return qs

        village = get_resident_location(user)

        if user.role == "leader":
            # Leader sees all events in their village
            return qs.filter(village=village) if village else qs.none()

        if user.role == "resident":
            # Resident sees only events they organized
            return qs.filter(organizer=user)

        # Default deny
        return qs.none()

    def get_object(self):
        """
        Enforce object-level permissions
        Allow anyone to access event details by ID
        """
        obj = super().get_object()
        user = self.request.user

        # Allow anyone to view event details (retrieve action)
        if self.action == 'retrieve':
            return obj

        # For other actions, enforce normal permissions
        if not user.is_authenticated:
            raise NotAuthenticated("You must be logged in.")

        # Check if user has a role attribute (AnonymousUser doesn't)
        if not hasattr(user, 'role'):
            raise PermissionDenied("Invalid user type.")

        village = get_resident_location(user)

        if user.role == "leader" and obj.village != village:
            raise PermissionDenied("Access denied to events from another village.")

        if user.role == "resident" and obj.organizer != user:
            raise PermissionDenied("You can only access your own events.")

        return obj

    def check_user_authentication(self):
        """Helper method to check if user is authenticated and has a role"""
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated("You must be logged in.")
        if not hasattr(user, 'role'):
            raise PermissionDenied("Invalid user type.")
        return user

    def perform_create(self, serializer):
        user = self.check_user_authentication()
        village = get_resident_location(user)

        if user.role in ["resident", "leader"]:
            if not village:
                raise PermissionDenied("You must be assigned to a village to create events.")
            serializer.save(organizer=user, village=village)
        elif user.role == "admin":
            # Admin can create events for any village
            village_data = serializer.validated_data.get('village')
            serializer.save(organizer=user, village=village_data)
        else:
            raise PermissionDenied("Invalid role")

    def perform_destroy(self, instance):
        user = self.check_user_authentication()
        village = get_resident_location(user)

        if user.role == "resident" and instance.organizer != user:
            raise PermissionDenied("You can only delete your own events.")

        if user.role == "leader" and instance.village != village:
            raise PermissionDenied("You cannot delete events from another village.")

        # Admin can delete anything
        instance.delete()

    # Disable full updates
    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT", detail="Updating events is disabled.")

    def perform_update(self, serializer):
        user = self.check_user_authentication()
        instance = self.get_object()

        # Restrict status updates to leader/admin
        if "status" in serializer.validated_data and user.role not in ["leader", "admin"]:
            raise PermissionDenied("Only leaders and admins can update the status.")

        # Leader can update status only for their village
        if user.role == "leader" and "status" in serializer.validated_data:
            village = get_resident_location(user)
            if instance.village != village:
                raise PermissionDenied("You cannot update status for events outside your village.")

        # Residents can update other fields only for their own events
        if user.role == "resident" and instance.organizer != user:
            raise PermissionDenied("You can only update your own events.")

        serializer.save()