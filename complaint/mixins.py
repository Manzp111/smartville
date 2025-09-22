from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from Resident.utils import get_resident_location

class ComplaintRolePermissionMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to access this resource.")

        if user.role == "admin":
            return qs

        location = get_resident_location(user)

        if user.role == "leader":
            return qs.filter(location=location) if location else qs.none()

        if user.role == "resident":
            return qs.filter(complainant=user.person)

        return qs.none()

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        location = get_resident_location(user)

        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in.")

        if user.role == "leader" and obj.location != location:
            raise PermissionDenied("Access denied to complaints from another village.")

        if user.role == "resident" and obj.complainant != user.person:
            raise PermissionDenied("You can only access your own complaints.")

        return obj

    def perform_create(self, serializer):
        user = self.request.user
        location = get_resident_location(user)

        if user.role in ["resident", "leader"]:
            if not location:
                raise PermissionDenied("You must be assigned to a village to submit complaints.")
            serializer.save(complainant=user.person, location=location)
        elif user.role == "admin":
            serializer.save()
        else:
            raise PermissionDenied("Invalid role")

    def perform_destroy(self, instance):
        user = self.request.user
        location = get_resident_location(user)

        if user.role == "resident" and instance.complainant != user.person:
            raise PermissionDenied("You can only delete your own complaints.")

        if user.role == "leader" and instance.location != location:
            raise PermissionDenied("You cannot delete complaints from another village.")

        instance.delete()

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT", detail="Updating complaints is disabled.")

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        if "status" in serializer.validated_data and user.role not in ["leader", "admin"]:
            raise PermissionDenied("Only leaders and admins can update the status.")

        if user.role == "leader" and "status" in serializer.validated_data:
            location = get_resident_location(user)
            if instance.location != location:
                raise PermissionDenied("You cannot update status for complaints outside your village.")

        if user.role == "resident" and instance.complainant != user.person:
            raise PermissionDenied("You can only update your own complaints.")

        serializer.save()