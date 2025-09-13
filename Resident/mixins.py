# account/permissions.py
from rest_framework.exceptions import PermissionDenied
from .utils import get_resident_location

class VillageRolePermissionMixin:
    """
    Handles permissions based on user roles:
    
    - Resident: Can access only objects they created
    - Leader: Can access all objects in their village
    - Admin: Can access all objects
    Assumes the model has 'added_by' and 'location' fields.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Admin can see everything
        if not user.is_authenticated:
            return qs.none() 

        if user.role == 'admin':
            return qs

        # Get the resident's village
        location = get_resident_location(user)

        if user.role == 'leader':
            # Leader sees everything in their village
            if location:
                return qs.filter(location=location)
            return qs.none()

        if user.role == 'resident':
            # Resident sees only their own posts
            return qs.filter(added_by=user)

        
        return qs.none()

    def perform_create(self, serializer):
        """
        Automatically assign added_by and location for new objects
        """
        user = self.request.user
        location = get_resident_location(user)

        if user.role == 'resident' or user.role == 'leader':
            if not location:
                raise PermissionDenied("You must be assigned to a village to create content.")
            serializer.save(added_by=user, location=location)
        elif user.role == 'admin':
            # Admin can assign any location manually
            serializer.save()
        else:
            raise PermissionDenied("Invalid role")

    def perform_update(self, serializer):
        user = self.request.user
        location = get_resident_location(user)

        # Resident can update only their own
        if user.role == 'resident' and serializer.instance.added_by != user:
            raise PermissionDenied("You can only modify your own content.")

        # Leader can update only objects in their village
        if user.role == 'leader' and serializer.instance.location != location:
            raise PermissionDenied("You cannot modify content from another village.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        location = get_resident_location(user)

        if user.role == 'resident' and instance.added_by != user:
            raise PermissionDenied("You can only delete your own content.")

        if user.role == 'leader' and instance.location != location:
            raise PermissionDenied("You cannot delete content from another village.")

        # Admin can delete anything
        instance.delete()
