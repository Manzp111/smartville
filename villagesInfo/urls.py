from django.urls import path
from .views import VillageNewsAPIView
from .suggetion_views import (
    SuggestionCreateView,
    SuggestionListView,
    SuggestionDetailView,
    SuggestionStatusUpdateView,
    SuggestionDeleteView,
    VoteAddView,
    VoteRemoveView,
    CommentCreateView,
    CommentListView,
)

urlpatterns = [
    path('suggestions/list', SuggestionListView.as_view(), name='suggestion-list'),
    path('suggestions/create', SuggestionCreateView.as_view(), name='suggestion-create'),
    path('suggestions/<uuid:suggestion_id>/', SuggestionDetailView.as_view(), name='suggestion-detail'),
    path('suggestions/<uuid:suggestion_id>/status/', SuggestionStatusUpdateView.as_view(), name='suggestion-status-update'),
    path('suggestions/<uuid:suggestion_id>/', SuggestionDeleteView.as_view(), name='suggestion-delete'),

    # Votes
    path('suggestions/<uuid:suggestion_id>/vote/', VoteAddView.as_view(), name='vote-add'),
    path('suggestions/<uuid:suggestion_id>/vote/', VoteRemoveView.as_view(), name='vote-remove'),

    # Comments
    path('suggestions/<uuid:suggestion_id>/comments/', CommentListView.as_view(), name='comment-list'),
    path('suggestions/<uuid:suggestion_id>/comments/', CommentCreateView.as_view(), name='comment-create'),

    path("village/<uuid:village_id>/news/", VillageNewsAPIView.as_view(), name="village-dashboard"),

]
