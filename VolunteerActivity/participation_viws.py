# VolunteerActivity/views.py

import uuid
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import VolunteerParticipation, VolunteeringEvent
from .participation_serializers import VolunteerParticipationSerializer, VolunteerParticipationCreateSerializer


# ---------------- Custom Paginator ----------------
class ParticipationPagination(PageNumberPagination):
    """
    Custom paginator with detailed metadata in the response.
    """
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Returns paginated response with metadata.
        """
        return Response({
            "success": True,
            "data": data,
            "meta": {
                "page": self.page.number,
                "limit": self.get_page_size(self.request),
                "total": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "has_next": self.page.has_next(),
                "has_prev": self.page.has_previous(),
            },
        })


# ---------------- Volunteer Participation ViewSet ----------------
class VolunteerParticipationViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage volunteer participations, including:
    - Listing participations with pagination and filters
    - Creating participation requests
    - Approving/rejecting participations (single and bulk)
    - Counting approved participants
    """
    queryset = VolunteerParticipation.objects.all()
    serializer_class = VolunteerParticipationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ParticipationPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return VolunteerParticipationCreateSerializer
        return VolunteerParticipationSerializer

    # ---------------- CREATE PARTICIPATION ----------------
    @extend_schema(
        summary="Create participation request",
        description="""
        Users can join a volunteering event. 
        Rules:
        1. Cannot join twice.
        2. Event must be approved.
        3. Event must belong to user's village.
        """,
        examples=[
            OpenApiExample(
                name="example",
                value={
                   
  "event": "5eae2916-5de7-4e84-a7dd-d76405aa9ac0",
  "notes": "string"

                },
            )
        ],
        request=VolunteerParticipationCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Participation created successfully",
                response=VolunteerParticipationSerializer,
                examples=[
                    OpenApiExample(
                        name="Success Example",
                        value={
                            "success": True,
                            "message": "Participation request created successfully",
                            "data": {
                                "participation_id": str(uuid.uuid4()),
                                "user": str(uuid.uuid4()),
                                "event": str(uuid.uuid4()),
                                "status": "PENDING",
                                "notes": "string",
                                "joined_at": "2025-09-20T14:47:10Z",
                                "updated_at": "2025-09-20T14:47:10Z",
                                "approved_at": None
                            }
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(description="Validation error")
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a participation request for a volunteering event.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user = request.user
            event = serializer.validated_data['event']

            # ---------------- Validation ----------------
            if event.participations.filter(user=user).exists():
                return Response({"success": False, "message": "You cannot join this event twice."}, status=400)

            user_village_ids = [res.village.id for res in getattr(user, 'residencies', user.residencies.none()).all()]
            if event.village.id not in user_village_ids:
                return Response({"success": False, "message": "You cannot join an event outside your village."}, status=400)

            if event.status != 'APPROVED':
                return Response({"success": False, "message": "You cannot join an event that is not approved."}, status=400)

            # ---------------- Create Participation ----------------
            with transaction.atomic():
                participation, created = VolunteerParticipation.objects.get_or_create(
                    user=user,
                    event=event,
                    defaults={'notes': serializer.validated_data.get('notes', '')}
                )

            output_serializer = VolunteerParticipationSerializer(participation)
            return Response({
                "success": True,
                "message": "Participation request created successfully",
                "data": output_serializer.data
            }, status=201)

        except serializers.ValidationError as e:
            detail = e.detail

            # If dict → get first error
            if isinstance(detail, dict):
                detail = list(detail.values())[0]

            # If still a list → take the first element
            if isinstance(detail, list):
                detail = detail[0]

            return Response({
                "success": False,
                "message": str(detail)
            }, status=status.HTTP_400_BAD_REQUEST)


    # ---------------- LIST PARTICIPATIONS ----------------
    @extend_schema(
        summary="List participations",
        description="Retrieve all participations with pagination. Filters: volunteer_id, village_id",
        parameters=[
            OpenApiParameter(name='volunteer_id', description='Filter by volunteering event UUID', required=False, type=OpenApiTypes.UUID),
            OpenApiParameter(name='village_id', description='Filter by village UUID', required=False, type=OpenApiTypes.UUID),
            OpenApiParameter(name='page', description='Page number for pagination', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='limit', description='Number of items per page', required=False, type=OpenApiTypes.INT),
        ],
        responses={200: VolunteerParticipationSerializer}
    )
    def list(self, request, *args, **kwargs):
        """
        List participations with optional filters:
        - volunteer_id: Filter by specific event UUID
        - village_id: Filter by village UUID
        """
        volunteer_id = request.query_params.get('volunteer_id')
        village_id = request.query_params.get('village_id')

        queryset = self.queryset

        if volunteer_id:
            queryset = queryset.filter(event__volunteer_id=volunteer_id)
        if village_id:
            queryset = queryset.filter(event__village__id=village_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "message": "Participations retrieved successfully", "data": serializer.data})

    # ---------------- APPROVE OR REJECT SINGLE PARTICIPATION ----------------
    @extend_schema(
        summary="Approve or reject a participation",
        description="Organizer, village leader, or admin can approve/reject a participation. PATCH `{'status':'APPROVED'}` or `{'status':'REJECTED'}`",
        request=None
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Approve or reject a single participation.
        """
        participation = self.get_object()
        user = request.user
        new_status = request.data.get('status')

        if not (participation.event.organizer == user or participation.event.village.leader == user or user.role == 'admin'):
            return Response({"success": False, "message": "You do not have permission to update this participation."}, status=403)

        if new_status not in ['APPROVED', 'REJECTED']:
            return Response({"success": False, "message": "Status must be 'APPROVED' or 'REJECTED'."}, status=400)

        participation.status = new_status
        participation.approved_at = timezone.now()
        participation.save()

        serializer = self.get_serializer(participation)
        return Response({
            "success": True,
            "message": f"Participation {new_status.lower()} successfully",
            "data": serializer.data
        })

    # ---------------- BULK APPROVE/REJECT PARTICIPATIONS ----------------
    @extend_schema(
        summary="Bulk approve or reject participations",
        description="""
        Approve or reject multiple participation requests by providing their UUIDs and the desired status.
        Permissions: Organizer of the event, village leader, or admin only.
        """,
        parameters=[
            OpenApiParameter(
                name='participation_ids',
                description='List of participation UUIDs',
                required=True,
                type=OpenApiTypes.UUID,
                many=True
            ),
            OpenApiParameter(
                name='status',
                description="Desired status: APPROVED or REJECTED",
                required=True,
                type=OpenApiTypes.STR
            ),
        ],
        responses={200: OpenApiResponse(description="Bulk update result")}
    )
    def bulk_update_status(self, request, *args, **kwargs):
        """
        Bulk approve or reject participations.
        """
        participation_ids = request.data.get('participation_ids')
        new_status = request.data.get('status')

        if not participation_ids or not isinstance(participation_ids, list):
            return Response({"success": False, "message": "participation_ids must be a list of UUIDs"}, status=400)

        if new_status not in ['APPROVED', 'REJECTED']:
            return Response({"success": False, "message": "status must be 'APPROVED' or 'REJECTED'."}, status=400)

        participations = VolunteerParticipation.objects.filter(participation_id__in=participation_ids)

        if not participations.exists():
            return Response({"success": False, "message": "No participations found for the provided IDs"}, status=404)

        updated = []
        skipped = []

        for participation in participations:
            user = request.user
            if not (participation.event.organizer == user or participation.event.village.leader == user or user.role == 'admin'):
                skipped.append(str(participation.participation_id))
                continue
            participation.status = new_status
            participation.approved_at = timezone.now()
            participation.save()
            updated.append(str(participation.participation_id))

        return Response({
            "success": True,
            "message": f"{new_status} status applied successfully",
            "updated_participations": updated,
            "skipped_participations": skipped
        })

    # ---------------- COUNT APPROVED ----------------
    @extend_schema(
        summary="Count approved participations",
        description="Returns number of approved participations for a given event UUID.",
        parameters=[
            OpenApiParameter(
                name='volunteer_id',
                description='UUID of the volunteering event',
                required=True,
                type=OpenApiTypes.UUID
            ),
        ],
        responses={200: OpenApiResponse(description="Approved participations count")}
    )
    def approved_count(self, request, *args, **kwargs):
        """
        Count approved participations for a specific volunteering event.
        """
        event_id = request.query_params.get('volunteer_id')
        if not event_id:
            return Response({"success": False, "message": "Please provide volunteer_id"}, status=400)

        count = VolunteerParticipation.objects.filter(event__volunteer_id=event_id, status='APPROVED').count()
        return Response({"success": True, "approved_count": count})
