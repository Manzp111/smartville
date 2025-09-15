# account/permissions.py
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from drf_spectacular.utils import extend_schema
from .tasks import send_new_resident_email
from account.models import User, Person
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

        if not user.is_authenticated:
            return qs.none()

        if user.role == 'admin':
            return qs

        location = get_resident_location(user)

        if user.role == 'leader':
            return qs.filter(location=location) if location else qs.none()

        if user.role == 'resident':
            return qs.filter(added_by=user)

        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        location = None

        # Determine location based on role
        if user.role in ["resident", "leader"]:
            if hasattr(user, 'residencies') and user.residencies.exists():
                location = user.residencies.first().location
            elif hasattr(user, 'led_villages') and user.led_villages.exists():
                location = user.led_villages.first()
            if not location:
                raise PermissionDenied("You must be assigned to a village to create a resident.")
        elif user.role == "admin":
            location = serializer.validated_data.get("location")
            if not location:
                raise PermissionDenied("Admin must specify location.")

        # Handle nested 'person' data
        person_data = serializer.validated_data.pop('person', None)
        if not person_data:
            raise PermissionDenied("Person data is required to create a resident.")

        person = Person.objects.create(
            first_name=person_data.get('first_name'),
            last_name=person_data.get('last_name'),
            phone_number=person_data.get('phone_number'),
            national_id=person_data.get('national_id'),
            gender=person_data.get('gender'),
            person_type='resident'
        )

        # Save Resident with person, location, added_by
        resident = serializer.save(
            person=person,
            location=location,
            added_by=user
        )

        # Notify village leader if exists
        if location and hasattr(location, 'leader') and location.leader and location.leader.email:
            send_new_resident_email.delay(
                leader_email=location.leader.email,
                resident_name=f"{resident.person.first_name} {resident.person.last_name}",
                village_name=f"{location.village}"
            )

    @extend_schema(exclude=True)
    def perform_update(self, serializer):
        raise MethodNotAllowed("PUT", detail="Updating events is disabled.")

    def perform_destroy(self, instance):
        user = self.request.user
        location = get_resident_location(user)

        if user.role == 'resident' and instance.added_by != user:
            raise PermissionDenied("You can only delete your own content.")

        if user.role == 'leader' and instance.location != location:
            raise PermissionDenied("You cannot delete content from another village.")

        # Admin can delete anything
        instance.delete()
