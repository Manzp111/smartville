# visitors/permissions.py
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from drf_spectacular.utils import extend_schema
from account.models import Person
from .models import Visitor
from Resident.utils import get_resident_location  # same util you used
from .tasks import send_new_visitor_email  # (optional) for leader notification


class VisitorRolePermissionMixin:
    """
    Permissions for Visitor model:
    
    - Resident: Can only see/add visitors they hosted.
    - Leader: Can see all visitors in their village.
    - Admin: Can see all visitors everywhere.
    Assumes model has 'host' (Resident) and 'visitor_location'.
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
            return qs.filter(visitor_location=location) if location else qs.none()

        if user.role == 'resident':
            return qs.filter(host__added_by=user)

        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        location = None

        # Find location for resident/leader
        if user.role in ["resident", "leader"]:
            if hasattr(user, 'residencies') and user.residencies.exists():
                location = user.residencies.first().location
            elif hasattr(user, 'led_villages') and user.led_villages.exists():
                location = user.led_villages.first()

            if not location:
                raise PermissionDenied("You must belong to a village to add a visitor.")

        elif user.role == "admin":
            location = serializer.validated_data.get("visitor_location")
            if not location:
                raise PermissionDenied("Admin must specify a visitor location.")

        # Handle nested person data (like for Resident)
        person_data = serializer.validated_data.pop('visitor_info', None)
        if not person_data:
            raise PermissionDenied("Visitor person data is required.")

        person = Person.objects.create(
            first_name=person_data.get('first_name'),
            last_name=person_data.get('last_name'),
            phone_number=person_data.get('phone_number'),
            national_id=person_data.get('national_id'),
            gender=person_data.get('gender'),
            person_type='visitor'
        )

        visitor = serializer.save(
            visitor_info=person,
            visitor_location=location,
            host=user.residencies.first() if user.role == "resident" else None
        )

        # Notify leader if exists
        if location and hasattr(location, 'leader') and location.leader and location.leader.email:
            send_new_visitor_email.delay(
                leader_email=location.leader.email,
                visitor_name=f"{visitor.visitor_info.first_name} {visitor.visitor_info.last_name}",
                host_name=str(visitor.host.person),
                village_name=f"{location.village}"
            )



    def perform_destroy(self, instance):
        user = self.request.user
        location = get_resident_location(user)

        if user.role == 'resident' and instance.host.added_by != user:
            raise PermissionDenied("You can only delete your own visitors.")

        if user.role == 'leader' and instance.visitor_location != location:
            raise PermissionDenied("You cannot delete visitors from another village.")

        # Admin can delete anything
        instance.delete()
