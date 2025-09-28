from rest_framework import serializers
from .models import Suggestion, Comment, Vote
from Village.serializers import LocationSerializer
from account.serializers import UserListSerializer


class CommentSerializer(serializers.ModelSerializer):
    # user_display = serializers.CharField(source="user.email", read_only=True)
    user=UserListSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["comment_id", "user", "text", "created_at"]
        read_only_fields = ["user", "created_at"]


class SuggestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    votes_count = serializers.IntegerField(source="votes.count", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    village=LocationSerializer(read_only=True)

    class Meta:
        model = Suggestion
        fields = [
            "suggestion_id", "title", "description", "category",
            "status", "is_anonymous", "author",
            "votes_count", "comments_count",
            "village", "created_at", "updated_at"
        ]
        read_only_fields = ["resident", "village"]

    def get_author(self, obj):
        return obj.author_display()


class SuggestionDetailSerializer(SuggestionSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(SuggestionSerializer.Meta):
        fields = SuggestionSerializer.Meta.fields + ["comments"]
