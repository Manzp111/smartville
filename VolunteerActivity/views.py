from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import VolunteeringEvent, VolunteerParticipation
from .serializers import (
    VolunteeringEventSerializer,
    VolunteeringEventCreateSerializer,
    VolunteerParticipationSerializer,
)
from Village.models import Village
from Resident.models import Resident
from .mixins import EventAccessPermission


class VolunteeringEventViewSet(EventAccessPermission, viewsets.ModelViewSet):
    queryset = VolunteeringEvent.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return VolunteeringEventCreateSerializer
        return VolunteeringEventSerializer

    def perform_create(self, serializer):
        user = self.request.user
        try:
            resident = Resident.objects.get(person=user.person, is_deleted=False)
        except Resident.DoesNotExist:
            raise ValueError("User is not linked to a resident")

        serializer.save(organizer=user, village=resident.village)

    def get_queryset(self):
        """
        Control access for list view:
        - Admin → all events
        - Leader → events in villages they lead
        - Resident → only events in their own village
        For retrieve (detail) → no restriction
        """
        user = self.request.user

        if self.action == "retrieve":
            # Allow viewing any event by ID
            return VolunteeringEvent.objects.all()

        # Restrict list view based on role
        if user.role == "admin":
            return VolunteeringEvent.objects.all()

        if user.role == "leader":
            return VolunteeringEvent.objects.filter(village__leader=user)

        if user.role == "resident":
            try:
                resident = Resident.objects.get(person=user.person, is_deleted=False)
                return VolunteeringEvent.objects.filter(village=resident.village)
            except Resident.DoesNotExist:
                return VolunteeringEvent.objects.none()

        return VolunteeringEvent.objects.none()



class VolunteerParticipationViewSet(viewsets.ModelViewSet):
    queryset = VolunteerParticipation.objects.all()
    serializer_class = VolunteerParticipationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        When a user joins an event:
        - Status = PENDING
        - User = logged in user
        """
        user = self.request.user
        event = serializer.validated_data["event"]

        # Prevent joining if already joined
        if VolunteerParticipation.objects.filter(user=user, event=event).exists():
            raise ValueError("You already requested to join this event")

        serializer.save(user=user, status="PENDING")

    def get_queryset(self):
        """
        Access control:
        - Admin → all participation records
        - Leader → participation in their villages
        - Resident → only their own participation
        """
        user = self.request.user

        if user.role == "admin":
            return VolunteerParticipation.objects.all()

        if user.role == "leader":
            return VolunteerParticipation.objects.filter(event__village__leader=user)

        if user.role == "resident":
            return VolunteerParticipation.objects.filter(user=user)

        return VolunteerParticipation.objects.none()

    # Custom actions for approval / rejection
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        participation = get_object_or_404(VolunteerParticipation, pk=pk)
        event = participation.event

        # Only organizer/leader/admin can approve
        if not (
            request.user == event.organizer
            or request.user.role in ["leader", "admin"]
        ):
            return Response(
                {"detail": "Not allowed to approve."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if event.is_full:
            return Response(
                {"detail": "Event is already full."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        participation.status = "APPROVED"
        participation.save()
        return Response({"detail": "Volunteer approved."})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        participation = get_object_or_404(VolunteerParticipation, pk=pk)
        event = participation.event

        if not (
            request.user == event.organizer
            or request.user.role in ["leader", "admin"]
        ):
            return Response(
                {"detail": "Not allowed to reject."},
                status=status.HTTP_403_FORBIDDEN,
            )

        participation.status = "REJECTED"
        participation.save()
        return Response({"detail": "Volunteer rejected."})
