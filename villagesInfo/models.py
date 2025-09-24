import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from Resident.models import Resident
from Village.models import Village


class SuggestionCategory(models.TextChoices):
    INFRASTRUCTURE = "infrastructure", "Infrastructure"
    COMMUNITY = "community", "Community"
    EDUCATION = "education", "Education"
    ENVIRONMENT = "environment", "Environment"
    HEALTH = "health", "Health"


class SuggestionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    IMPLEMENTED = "implemented", "Implemented"
    REJECTED = "rejected", "Rejected"


class Suggestion(models.Model):
    suggestion_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name="suggestions")
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name="suggestions")
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=SuggestionCategory.choices)
    status = models.CharField(max_length=50, choices=SuggestionStatus.choices, default=SuggestionStatus.PENDING)
    is_anonymous = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def author_display(self):
        return "Anonymous" if self.is_anonymous else str(self.resident.person)

    def __str__(self):
        return f"{self.title} ({self.village.village})"


class Vote(models.Model):
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("suggestion", "user")  # prevent duplicate votes


class Comment(models.Model):
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user} on {self.suggestion}"
