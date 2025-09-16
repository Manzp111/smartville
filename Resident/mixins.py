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
    Assumes the model has 'added_by' and 'Location' fields.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.role == 'admin':
            return qs

        Location = get_resident_location(user)

        if user.role == 'leader':
            return qs.filter(Location=Location) if Location else qs.none()

        if user.role == 'resident':
            return qs.filter(added_by=user)

        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        Location = None

        # Determine Location based on role
        if user.role in ["resident", "leader"]:
            if hasattr(user, 'residencies') and user.residencies.exists():
                Location = user.residencies.first().Location
            elif hasattr(user, 'led_villages') and user.led_villages.exists():
                Location = user.led_villages.first()
            if not Location:
                raise PermissionDenied("You must be assigned to a village to create a resident.")
        elif user.role == "admin":
            Location = serializer.validated_data.get("Location")
            if not Location:
                raise PermissionDenied("Admin must specify Location.")

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

        # Save Resident with person, Location, added_by
        resident = serializer.save(
            person=person,
            Location=Location,
            added_by=user
        )

        # Notify village leader if exists
        if Location and hasattr(Location, 'leader') and Location.leader and Location.leader.email:
            send_new_resident_email.delay(
                leader_email=Location.leader.email,
                resident_name=f"{resident.person.first_name} {resident.person.last_name}",
                village_name=f"{Location.village}"
            )

    @extend_schema(exclude=True)
    def perform_update(self, serializer):
        raise MethodNotAllowed("PUT", detail="Updating events is disabled.")

    def perform_destroy(self, instance):
        user = self.request.user
        Location = get_resident_location(user)

        if user.role == 'resident' and instance.added_by != user:
            raise PermissionDenied("You can only delete your own content.")

        if user.role == 'leader' and instance.Location != Location:
            raise PermissionDenied("You cannot delete content from another village.")

        # Admin can delete anything
        instance.delete()
