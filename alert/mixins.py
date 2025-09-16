from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from drf_spectacular.utils import extend_schema
from Resident.utils import get_resident_location

class AlertRolePermissionMixin:
    """
    Handles Alert access based on user roles:
    - Admin: full access
    - Leader: access restricted to their village
    - Resident: access only to alerts they reported
    - Anonymous: no access
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to access this resource.")

        if user.role == "admin":
            return qs

        location = get_resident_location(user)

        if user.role == "leader":
            return qs.filter(village=location) if location else qs.none()

        if user.role == "resident":
            return qs.filter(reporter=user)

        return qs.none()

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        location = get_resident_location(user)

        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in.")

        if user.role == "leader" and obj.village != location:
            raise PermissionDenied("Access denied to alerts from another village.")

        if user.role == "resident" and obj.reporter != user:
            raise PermissionDenied("You can only access your own alerts.")

        return obj

    def perform_create(self, serializer):
        user = self.request.user
        location = get_resident_location(user)

        if user.role in ["resident", "leader"]:
            if not location:
                raise PermissionDenied("You must be assigned to a village to report alerts.")
            serializer.save(reporter=user, village=location)
        elif user.role == "admin":
            serializer.save()
        else:
            raise PermissionDenied("Invalid role")

    def perform_destroy(self, instance):
        user = self.request.user
        location = get_resident_location(user)

        if user.role == "resident" and instance.reporter != user:
            raise PermissionDenied("You can only delete your own alerts.")

        if user.role == "leader" and instance.village != location:
            raise PermissionDenied("You cannot delete alerts from another village.")

        instance.delete()

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT", detail="Updating alerts is disabled.")

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        # Only leader/admin can update status
        if "status" in serializer.validated_data and user.role not in ["leader", "admin"]:
            raise PermissionDenied("Only leaders and admins can update the status.")

        if user.role == "leader" and "status" in serializer.validated_data:
            location = get_resident_location(user)
            if instance.village != location:
                raise PermissionDenied("You cannot update status for alerts outside your village.")

        if user.role == "resident" and instance.reporter != user:
            raise PermissionDenied("You can only update your own alerts.")

        serializer.save()