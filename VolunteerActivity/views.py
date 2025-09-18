from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes, OpenApiResponse
from django.utils import timezone
from django.db import models
from rest_framework import serializers

from .models import VolunteeringEvent, VolunteerParticipation
from .serializers import (
    VolunteeringEventSerializer,
    VolunteeringEventCreateSerializer,
    VolunteerParticipationSerializer,
    VolunteerParticipationCreateSerializer,
    EventApprovalSerializer,
)
from .mixins import IsApprovedResident, CanManageEvent
from .pagination import StandardResultsSetPagination
from Resident.models import Resident
from Village.models import Village

@extend_schema_view(
    list=extend_schema(
        summary="List volunteering events",
        description="Retrieve a list of volunteering events based on user role and permissions.",
        parameters=[
            OpenApiParameter(name='status', description='Filter by event status', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='village', description='Filter by village ID', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='date', description='Filter by date', required=False, type=OpenApiTypes.DATE),
        ],
        responses={
            200: VolunteeringEventSerializer(many=True),
            403: OpenApiResponse(description="Forbidden - User not authenticated or not approved resident"),
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve volunteering event",
        description="Get detailed information about a specific volunteering event.",
        responses={
            200: VolunteeringEventSerializer,
            404: OpenApiResponse(description="Event not found"),
            403: OpenApiResponse(description="Forbidden - User not authenticated or not approved resident"),
        }
    ),
    create=extend_schema(
        summary="Create volunteering event",
        description="Create a new volunteering event. Residents can only create events for their own village.",
        request=VolunteeringEventCreateSerializer,
        responses={
            201: VolunteeringEventSerializer,
            400: OpenApiResponse(description="Bad request - Invalid data"),
            403: OpenApiResponse(description="Forbidden - User not authenticated or not approved resident"),
        }
    ),
    update=extend_schema(
        summary="Update volunteering event",
        description="Update an existing volunteering event. Only organizers and authorized users can update events.",
        request=VolunteeringEventCreateSerializer,
        responses={
            200: VolunteeringEventSerializer,
            400: OpenApiResponse(description="Bad request - Invalid data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to update this event"),
            404: OpenApiResponse(description="Event not found"),
        }
    ),
    partial_update=extend_schema(
        summary="Partial update volunteering event",
        description="Partially update an existing volunteering event.",
        request=VolunteeringEventCreateSerializer,
        responses={
            200: VolunteeringEventSerializer,
            400: OpenApiResponse(description="Bad request - Invalid data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to update this event"),
            404: OpenApiResponse(description="Event not found"),
        }
    ),
    destroy=extend_schema(
        summary="Delete volunteering event",
        description="Delete a volunteering event. Only organizers and authorized users can delete events.",
        responses={
            204: OpenApiResponse(description="Event deleted successfully"),
            403: OpenApiResponse(description="Forbidden - User not authorized to delete this event"),
            404: OpenApiResponse(description="Event not found"),
        }
    )
)
class VolunteeringEventViewSet(viewsets.ModelViewSet):
    serializer_class = VolunteeringEventSerializer
    permission_classes = [IsAuthenticated, IsApprovedResident]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'village', 'date']

    def get_queryset(self):
        user = self.request.user
        queryset = VolunteeringEvent.objects.select_related('village', 'organizer')

        if self.action == "retrieve":
            return queryset

        if user.role == "admin":
            return queryset

        if user.role == "leader":
            return queryset.filter(village__leader=user)

        if user.role == "resident":
            try:
                resident = Resident.objects.get(person=user.person, is_deleted=False)
                # Residents see approved events + their own events
                return queryset.filter(
                    village=resident.village
                ).filter(
                    models.Q(status='APPROVED') | models.Q(organizer=user)
                )
            except Resident.DoesNotExist:
                return queryset.none()

        return queryset.none()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return VolunteeringEventCreateSerializer
        return VolunteeringEventSerializer

    def perform_create(self, serializer):
        user = self.request.user
        resident = Resident.objects.get(person=user.person, is_deleted=False)
        serializer.save(organizer=user, village=resident.village, status='PENDING')

    @extend_schema(
        summary="Submit event for approval",
        description="Submit a draft event for approval by village leaders or admins.",
        responses={
            200: OpenApiResponse(description="Event submitted for approval successfully"),
            400: OpenApiResponse(description="Bad request - Only draft events can be submitted"),
            403: OpenApiResponse(description="Forbidden - User not authorized to manage this event"),
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[CanManageEvent])
    def submit_for_approval(self, request, pk=None):
        """Submit draft event for approval"""
        volunteering_event = self.get_object()
        
        if volunteering_event.status != 'DRAFT':
            return Response(
                {"detail": "Only draft events can be submitted for approval."},
                status=status.HTTP_400_BAD_REQUEST
            )

        volunteering_event.status = 'PENDING'
        volunteering_event.save()
        
        return Response(
            {"detail": "Event submitted for approval successfully."},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Approve event",
        description="Approve a pending event. Only village leaders and admins can approve events.",
        request=EventApprovalSerializer,
        responses={
            200: OpenApiResponse(description="Event approved successfully"),
            400: OpenApiResponse(description="Bad request - Only pending events can be approved or invalid data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to manage this event"),
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[CanManageEvent])
    def approve(self, request, pk=None):
        """Approve an event"""
        volunteering_event = self.get_object()
        serializer = EventApprovalSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if volunteering_event.status != 'PENDING':
            return Response(
                {"detail": "Only pending events can be approved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        volunteering_event.status = 'APPROVED'
        volunteering_event.approved_at = timezone.now()
        volunteering_event.rejection_reason = None
        volunteering_event.save()
        
        return Response(
            {"detail": "Event approved successfully."},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Reject event",
        description="Reject a pending event. Only village leaders and admins can reject events.",
        request=EventApprovalSerializer,
        responses={
            200: OpenApiResponse(description="Event rejected successfully"),
            400: OpenApiResponse(description="Bad request - Only pending events can be rejected or invalid data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to manage this event"),
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[CanManageEvent])
    def reject(self, request, pk=None):
        """Reject an event"""
        volunteering_event = self.get_object()
        serializer = EventApprovalSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if volunteering_event.status != 'PENDING':
            return Response(
                {"detail": "Only pending events can be rejected."},
                status=status.HTTP_400_BAD_REQUEST
            )

        volunteering_event.status = 'REJECTED'
        volunteering_event.rejection_reason = serializer.validated_data.get('rejection_reason', '')
        volunteering_event.save()
        
        return Response(
            {"detail": "Event rejected successfully."},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Join event",
        description="Join an approved volunteering event as a participant.",
        request=VolunteerParticipationCreateSerializer,
        responses={
            201: OpenApiResponse(description="Join request submitted successfully"),
            400: OpenApiResponse(description="Bad request - Event not joinable or user already joined"),
            403: OpenApiResponse(description="Forbidden - User not authenticated or not approved resident"),
        }
    )
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join an event"""
        volunteering_event = self.get_object()
        user = request.user

        if volunteering_event.status != 'APPROVED':
            return Response(
                {"detail": "Only approved events can be joined."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not volunteering_event.is_joinable:
            return Response(
                {"detail": "This event is not available for joining."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if volunteering_event.has_user_participation(user):
            current_status = volunteering_event.get_user_participation_status(user)
            return Response(
                {"detail": f"You already have a {current_status.lower()} request for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        participation_data = {'event': volunteering_event.volunteer_id, 'notes': request.data.get('notes', '')}
        serializer = VolunteerParticipationCreateSerializer(
            data=participation_data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                {"detail": "Your request to join has been submitted for approval."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="List volunteer event participants",
        description="Get a paginated list of participants for a specific volunteer event. Only volunteer event organizers and authorized users can view participants.",
        responses={
            200: VolunteerParticipationSerializer(many=True),
            403: OpenApiResponse(description="Forbidden - User not authorized to view participants"),
            404: OpenApiResponse(description="Volunteering Event not found"),
        }
    )
    @action(detail=True, methods=['get'], permission_classes=[CanManageEvent])
    def participants(self, request, pk=None):
        """Get volunteer event participants with pagination"""
        volunteering_event = self.get_object()
        participants = volunteering_event.participations.select_related('user').all()
        
        page = self.paginate_queryset(participants)
        if page is not None:
            serializer = VolunteerParticipationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = VolunteerParticipationSerializer(participants, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List volunteer participations",
        description="Retrieve a list of volunteer participation requests based on user role and permissions.",
        responses={
            200: VolunteerParticipationSerializer(many=True),
            403: OpenApiResponse(description="Forbidden - User not authenticated"),
        }
    ),
    retrieve=extend_schema(
        summary="Retrieve participation",
        description="Get detailed information about a specific volunteer participation.",
        responses={
            200: VolunteerParticipationSerializer,
            404: OpenApiResponse(description="Participation not found"),
            403: OpenApiResponse(description="Forbidden - User not authorized to view this participation"),
        }
    ),
    create=extend_schema(
        summary="Create participation request",
        description="Create a new volunteer participation request for an approved event.",
        request=VolunteerParticipationCreateSerializer,
        responses={
            201: VolunteerParticipationSerializer,
            400: OpenApiResponse(description="Bad request - Invalid data or event not joinable"),
            403: OpenApiResponse(description="Forbidden - User not authenticated"),
        }
    ),
    update=extend_schema(
        summary="Update participation",
        description="Update an existing volunteer participation. Only authorized users can update participations.",
        request=VolunteerParticipationCreateSerializer,
        responses={
            200: VolunteerParticipationSerializer,
            400: OpenApiResponse(description="Bad request - Invalid data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to update this participation"),
            404: OpenApiResponse(description="Participation not found"),
        }
    ),
    partial_update=extend_schema(
        summary="Partial update participation",
        description="Partially update an existing volunteer participation.",
        request=VolunteerParticipationCreateSerializer,
        responses={
            200: VolunteerParticipationSerializer,
            400: OpenApiResponse(description="Bad request - Invalid data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to update this participation"),
            404: OpenApiResponse(description="Participation not found"),
        }
    ),
    destroy=extend_schema(
        summary="Delete participation",
        description="Delete a volunteer participation. Only authorized users can delete participations.",
        responses={
            204: OpenApiResponse(description="Participation deleted successfully"),
            403: OpenApiResponse(description="Forbidden - User not authorized to delete this participation"),
            404: OpenApiResponse(description="Participation not found"),
        }
    )
)
class VolunteerParticipationViewSet(viewsets.ModelViewSet):
    serializer_class = VolunteerParticipationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "admin":
            return VolunteerParticipation.objects.select_related('user', 'event')
        
        if user.role == "leader":
            return VolunteerParticipation.objects.filter(
                event__village__leader=user
            ).select_related('user', 'event')
        
        if user.role == "resident":
            return VolunteerParticipation.objects.filter(
                user=user
            ).select_related('user', 'event')
        
        return VolunteerParticipation.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return VolunteerParticipationCreateSerializer
        return VolunteerParticipationSerializer

    def perform_create(self, serializer):
        user = self.request.user
        event = serializer.validated_data["event"]

        if event.status != 'APPROVED':
            raise serializers.ValidationError("Only approved events can be joined")

        if VolunteerParticipation.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError("You already requested to join this event")

        serializer.save(user=user, status="PENDING")

    @extend_schema(
        summary="Approve participation",
        description="Approve a pending volunteer participation request. Only event organizers and authorized users can approve participations.",
        request=EventApprovalSerializer,
        responses={
            200: OpenApiResponse(description="Volunteer approved successfully"),
            400: OpenApiResponse(description="Bad request - Only pending participations can be approved or event is full"),
            403: OpenApiResponse(description="Forbidden - User not authorized to manage this participation"),
        }
    )
    @action(detail=True, methods=["post"], permission_classes=[CanManageEvent])
    def approve(self, request, pk=None):
        participation = self.get_object()
        
        if participation.status != 'PENDING':
            return Response(
                {"detail": "Only pending participations can be approved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if participation.event.is_full:
            return Response(
                {"detail": "Event is already full."},
                status=status.HTTP_400_BAD_REQUEST
            )

        participation.status = "APPROVED"
        participation.approved_at = timezone.now()
        participation.save()
        
        return Response(
            {"detail": "Volunteer approved successfully."},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Reject participation",
        description="Reject a pending volunteer participation request. Only event organizers and authorized users can reject participations.",
        request=EventApprovalSerializer,
        responses={
            200: OpenApiResponse(description="Volunteer rejected successfully"),
            400: OpenApiResponse(description="Bad request - Only pending participations can be rejected or invalid data"),
            403: OpenApiResponse(description="Forbidden - User not authorized to manage this participation"),
        }
    )
    @action(detail=True, methods=["post"], permission_classes=[CanManageEvent])
    def reject(self, request, pk=None):
        participation = self.get_object()
        serializer = EventApprovalSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if participation.status != 'PENDING':
            return Response(
                {"detail": "Only pending participations can be rejected."},
                status=status.HTTP_400_BAD_REQUEST
            )

        participation.status = "REJECTED"
        participation.save()
        
        return Response(
            {"detail": "Volunteer rejected successfully."},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Withdraw participation",
        description="Withdraw your own participation request. Users can only withdraw their own pending requests.",
        responses={
            200: OpenApiResponse(description="Participation request withdrawn successfully"),
            400: OpenApiResponse(description="Bad request - Cannot withdraw approved participation"),
            403: OpenApiResponse(description="Forbidden - User can only withdraw their own requests"),
        }
    )
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """Withdraw participation request"""
        participation = self.get_object()
        user = request.user

        if participation.user != user:
            return Response(
                {"detail": "You can only withdraw your own participation requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        if participation.status == 'APPROVED':
            return Response(
                {"detail": "Cannot withdraw an approved participation. Please contact the organizer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        participation.delete()
        return Response(
            {"detail": "Participation request withdrawn successfully."},
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    list=extend_schema(
        summary="List village events",
        description="Retrieve a list of approved volunteering events for a specific village.",
        parameters=[
            OpenApiParameter(name='page_size', description='Number of results per page', required=False, type=OpenApiTypes.INT),
        ],
        responses={
            200: VolunteeringEventSerializer(many=True),
            404: OpenApiResponse(description="Village not found"),
        }
    )
)
class VillageEventViewSet(viewsets.ViewSet):
    pagination_class = StandardResultsSetPagination
     
    def list(self, request, village_id=None):
        """List approved volunteering events of a specific village"""
        try:
            village = Village.objects.get(village_id=village_id)
        except Village.DoesNotExist:
            return Response(
                {"detail": "Village not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        events = VolunteeringEvent.objects.filter(
            village=village, 
            status='APPROVED',
            date__gte=timezone.now().date()
        ).select_related('village', 'organizer')
        
        paginator = self.pagination_class()
        paginator.page_size = int(request.query_params.get("page_size", 10))
        result_page = paginator.paginate_queryset(events, request)
        
        serializer = VolunteeringEventSerializer(
            result_page, 
            many=True, 
            context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)

#############


class VillageEventViewSet(viewsets.ViewSet):
     
    def list(self, request, village_id=None):
        """List volunteering events of a specific village"""
        try:
            village = Village.objects.get(village_id=village_id)
        except Village.DoesNotExist:
            return Response({"detail": "Village not found"}, status=status.HTTP_404_NOT_FOUND)

        volunter_activity = VolunteeringEvent.objects.filter(village=village)
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("page_size", 10)  # allow custom page size
        result_page = paginator.paginate_queryset(volunter_activity, request)
        serializer = VolunteeringEventSerializer(volunter_activity, many=True)
        return Response({
            "status": "success",
            "message": f"Events for village {village.village}",
            "count": len(serializer.data),
            "data": serializer.data
        })