from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Suggestion, Vote, Comment
from .suggetion_serializers import SuggestionSerializer, SuggestionDetailSerializer, CommentSerializer

# ----------------------------
# 1. POST /api/suggestions → Create a new suggestion
# ----------------------------
@extend_schema(
    summary="Create a new suggestion",
    description="Authenticated resident can create a new suggestion linked to their village.",
    request=SuggestionSerializer,
    responses={
        201: OpenApiResponse(response=SuggestionSerializer, description="Suggestion created successfully"),
        400: OpenApiResponse(description="Validation error"),
        401: OpenApiResponse(description="Authentication required")
    },
    examples=[
        OpenApiExample(
            "Create Suggestion Example",
            value={
                "title": "Install Solar Street Lights",
                "description": "Better lighting is needed for safety during evening hours.",
                "category": "infrastructure"
            },
            request_only=True
        )
    ],
    tags=["Suggestions"]
)
class SuggestionCreateView(generics.CreateAPIView):
    serializer_class = SuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        resident = self.request.user.person.residencies.first()
        serializer.save(resident=resident, village=resident.village)


# ----------------------------
# 2. GET /api/suggestions → List suggestions (filter by status/category)
# ----------------------------
@extend_schema(
    summary="List suggestions",
    description="Retrieve a list of suggestions. Optional query params: status, category.",
    responses={
        200: OpenApiResponse(response=SuggestionSerializer, description="List of suggestions"),
        401: OpenApiResponse(description="Authentication required")
    },
    examples=[
        OpenApiExample(
            "List Suggestions Example",
            value=[
                {"title": "Community Garden", "status": "approved", "category": "community"},
                {"title": "Youth Skills Training", "status": "pending", "category": "education"}
            ],
            response_only=True
        )
    ],
    tags=["Suggestions"]
)
class SuggestionListView(generics.ListAPIView):
    serializer_class = SuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Suggestion.objects.all().order_by("-created_at")
        status_param = self.request.query_params.get("status")
        category_param = self.request.query_params.get("category")
        if status_param:
            queryset = queryset.filter(status=status_param)
        if category_param:
            queryset = queryset.filter(category=category_param)
        return queryset


# ----------------------------
# 3. GET /api/suggestions/:id → View single suggestion
# ----------------------------
@extend_schema(
    summary="Retrieve a single suggestion",
    description="Get detailed information for a single suggestion, including votes and comments.",
    responses={
        200: OpenApiResponse(response=SuggestionDetailSerializer, description="Suggestion details"),
        404: OpenApiResponse(description="Suggestion not found"),
        401: OpenApiResponse(description="Authentication required")
    },
    examples=[
        OpenApiExample(
            "Suggestion Detail Example",
            value={
                "suggestion_id": "uuid123",
                "title": "Improve Waste Collection",
                "description": "Collection is only once a week; needs improvement.",
                "status": "under_review",
                "votes": 67,
                "comments": [{"user": "Anonymous", "text": "Important!"}]
            },
            response_only=True
        )
    ],
    tags=["Suggestions"]
)
class SuggestionDetailView(generics.RetrieveAPIView):
    serializer_class = SuggestionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "suggestion_id"

    def get_queryset(self):
        return Suggestion.objects.all()


# ----------------------------
# 4. PATCH /api/suggestions/:id/status → Update status (admin/leader only)
# ----------------------------
@extend_schema(
    summary="Update suggestion status",
    description="Admin or village leader can update the status of a suggestion (pending, approved, rejected, implemented).",
    request={
        "application/json": {"type": "object", "properties": {"status": {"type": "string", "example": "approved"}}}
    },
    responses={
        200: OpenApiResponse(description="Status updated successfully"),
        400: OpenApiResponse(description="Invalid status"),
        403: OpenApiResponse(description="Not authorized"),
        404: OpenApiResponse(description="Suggestion not found")
    },
    tags=["Suggestions"]
)
class SuggestionStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, suggestion_id):
        suggestion = get_object_or_404(Suggestion, suggestion_id=suggestion_id)
        if request.user.role not in ["admin", "leader"]:
            return Response({"detail": "Not authorized"}, status=403)
        new_status = request.data.get("status")
        if new_status not in dict(Suggestion._meta.get_field("status").choices):
            return Response({"detail": "Invalid status"}, status=400)
        suggestion.status = new_status
        suggestion.save()
        return Response({"success": True, "message": "Status updated"})


# ----------------------------
# 5. DELETE /api/suggestions/:id → Delete suggestion (admin only)
# ----------------------------
@extend_schema(
    summary="Delete suggestion",
    description="Admin can permanently delete a suggestion.",
    responses={
        200: OpenApiResponse(description="Suggestion deleted successfully"),
        403: OpenApiResponse(description="Not authorized"),
        404: OpenApiResponse(description="Suggestion not found")
    },
    tags=["Suggestions"]
)
class SuggestionDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, suggestion_id):
        suggestion = get_object_or_404(Suggestion, suggestion_id=suggestion_id)
        if request.user.role != "admin":
            return Response({"detail": "Not authorized"}, status=403)
        suggestion.delete()
        return Response({"success": True, "message": "Suggestion deleted"})


# ----------------------------
# 6. POST /api/suggestions/:id/vote → Add a vote
# ----------------------------
@extend_schema(
    summary="Add a vote to a suggestion",
    description="Authenticated users can vote for a suggestion.",
    responses={200: OpenApiResponse(description="Vote added successfully"), 401: OpenApiResponse(description="Authentication required")},
    tags=["Votes"]
)
class VoteAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, suggestion_id):
        suggestion = get_object_or_404(Suggestion, suggestion_id=suggestion_id)
        Vote.objects.get_or_create(suggestion=suggestion, user=request.user)
        return Response({"success": True, "message": "Vote added"})


# ----------------------------
# 7. DELETE /api/suggestions/:id/vote → Remove a vote
# ----------------------------
@extend_schema(
    summary="Remove a vote from a suggestion",
    description="Authenticated users can remove their vote from a suggestion.",
    responses={200: OpenApiResponse(description="Vote removed successfully"), 401: OpenApiResponse(description="Authentication required")},
    tags=["Votes"]
)
class VoteRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, suggestion_id):
        suggestion = get_object_or_404(Suggestion, suggestion_id=suggestion_id)
        Vote.objects.filter(suggestion=suggestion, user=request.user).delete()
        return Response({"success": True, "message": "Vote removed"})


# ----------------------------
# 8. POST /api/suggestions/:id/comments → Add a comment
# ----------------------------
@extend_schema(
    summary="Add a comment",
    description="Authenticated users can add a comment to a suggestion.",
    request=CommentSerializer,
    responses={
        201: OpenApiResponse(response=CommentSerializer, description="Comment created successfully"),
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Suggestion not found")
    },
    tags=["Comments"]
)
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        suggestion_id = self.kwargs["suggestion_id"]
        suggestion = get_object_or_404(Suggestion, suggestion_id=suggestion_id)
        serializer.save(user=self.request.user, suggestion=suggestion)


# ----------------------------
# 9. GET /api/suggestions/:id/comments → List comments
# ----------------------------
@extend_schema(
    summary="List comments",
    description="Retrieve all comments for a suggestion.",
    responses={
        200: OpenApiResponse(response=CommentSerializer, description="List of comments"),
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Suggestion not found")
    },
    tags=["Comments"]
)
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        suggestion_id = self.kwargs["suggestion_id"]
        return Comment.objects.filter(suggestion__suggestion_id=suggestion_id)
