# event/mixins.py
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from drf_spectacular.utils import extend_schema
from Resident.utils import get_resident_location

class EventRolePermissionMixin:
    """
    Handles Event access based on user roles:
    - Admin: full access
    - Leader: access restricted to their village
    - Resident: access only to events they organized
    - Anonymous: no access

    Also disables updates (PUT/PATCH) and enforces access control on object retrieval.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Anonymous users cannot access anything
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to access this resource.")

        if user.role == "admin":
            return qs

        location = get_resident_location(user)

        if user.role == "leader":
            # Leader sees all events in their village
            return qs.filter(village=location) if location else qs.none()

        if user.role == "resident":
            # Resident sees only events they organized
            return qs.filter(organizer=user)

        # Default deny
        return qs.none()

    def get_object(self):
        """
        Enforce object-level permissions for detail endpoints
        """
        obj = super().get_object()
        user = self.request.user
        location = get_resident_location(user)

        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in.")

        if user.role == "leader" and obj.village != location:
            raise PermissionDenied("Access denied to events from another village.")

        if user.role == "resident" and obj.organizer != user:
            raise PermissionDenied("You can only access your own events.")

        return obj

    def perform_create(self, serializer):
        user = self.request.user
        location = get_resident_location(user)

        if user.role in ["resident", "leader"]:
            if not location:
                raise PermissionDenied("You must be assigned to a village to create events.")
            serializer.save(organizer=user, village=location)
        elif user.role == "admin":
            serializer.save()
        else:
            raise PermissionDenied("Invalid role")

    def perform_destroy(self, instance):
        user = self.request.user
        location = get_resident_location(user)

        if user.role == "resident" and instance.organizer != user:
            raise PermissionDenied("You can only delete your own events.")

        if user.role == "leader" and instance.village != location:
            raise PermissionDenied("You cannot delete events from another village.")

        # Admin can delete anything
        instance.delete()

    # Disable updates completely
    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT", detail="Updating events is disabled.")

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH", detail="Updating events is disabled.")
