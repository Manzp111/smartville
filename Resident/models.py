from django.db import models
from account.models import Person, User
from Location.models import Location
import uuid
from django.utils import timezone


STATUS_CHOICES = [
    ("PENDING", "Pending Approval"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
]

class Resident(models.Model):
    resident_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="residencies")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="residents")
    has_account = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="added_residents")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    
    # Soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def soft_delete(self):
        """Mark this resident as deleted instead of removing from database."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a previously soft-deleted resident."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"{self.person} @ {self.location.village}"
