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
    Assumes the model has 'added_by' and 'Village' fields.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.role == 'admin':
            return qs

        village = get_resident_location(user)

        if user.role == 'leader':
            return qs.filter(village=village) if village else qs.none()

        if user.role == 'resident':
            return qs.filter(added_by=user)

        return qs.none()



    def perform_create(self, serializer):
        user = self.request.user
        village = None

        # Determine the village based on role
        if user.role == "resident":
            if user.person:
                active_residency = user.person.residencies.filter(is_deleted=False).first()
                if active_residency:
                    village = active_residency.village
            if not village:
                # Optionally allow specifying village explicitly
                village = serializer.validated_data.get("village")
                if not village:
                    raise PermissionDenied("You must be assigned to a village or specify one to create a resident.")

        elif user.role == "leader":
            led_village = user.led_villages.first()  # leader can have only one village
            if led_village:
                village = led_village
            else:
                raise PermissionDenied("You must lead a village to create a resident.")

        elif user.role == "admin":
            village = serializer.validated_data.get("village")
            if not village:
                raise PermissionDenied("Admin must specify a village.")

        # Handle nested 'person' data
        person_data = serializer.validated_data.pop('person', None)
        if not person_data:
            raise PermissionDenied("Person data is required to create a resident.")

        # Create a Person record
        person = Person.objects.create(
            first_name=person_data.get('first_name'),
            last_name=person_data.get('last_name'),
            phone_number=person_data.get('phone_number'),
            national_id=person_data.get('national_id'),
            gender=person_data.get('gender'),
            person_type='resident'
        )

        # Save Resident with person, village, added_by
        resident = serializer.save(
            person=person,
            village=village,
            added_by=user
        )


    # @extend_schema(exclude=True)
    # def perform_update(self, serializer):
    #     raise MethodNotAllowed("PUT", detail="Updating events is disabled.")

    def perform_destroy(self, instance):
        user = self.request.user
        Village = get_resident_location(user)

        if user.role == 'resident' and instance.added_by != user:
            raise PermissionDenied("You can only delete your own content.")

        if user.role == 'leader' and instance.Village != Village:
            raise PermissionDenied("You cannot delete content from another village.")

        # Admin can delete anything
        instance.delete()
