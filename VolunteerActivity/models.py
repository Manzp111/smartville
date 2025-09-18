import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError


class VolunteeringEvent(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PENDING", "Pending Approval"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]
    VOLUNTEER_EVENT_CATEGORY = [
        ("Community & Social", "Community & Social"),
        ("Health & Wellness", "Health & Wellness"),
        ("Education & Skills", "Education & Skills"),
        ("Environmental & Sustainability", "Environmental & Sustainability"),
        ("Safety & Emergency", "Safety & Emergency"),
        ("Economic & Livelihood", "Economic & Livelihood"),
        ("Special / One-Off Events", "Special / One-Off Events"),
        ("Civic & Governance", "Civic & Governance"),
    ]

    
    volunteer_id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False,unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField(null=True,blank=True)
    end_time = models.TimeField(null=True, blank=True)

    # end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=10)
    village = models.ForeignKey('Village.Village', on_delete=models.CASCADE, related_name="events")
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizer_of_volunteer_events")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    rejection_reason = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    skills_required = models.TextField(blank=True, null=True)
    category=models.CharField(max_length=50,choices=VOLUNTEER_EVENT_CATEGORY,default="Community & Social")
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = "Volunteering Event"
        verbose_name_plural = "Volunteering Events"

    def clean(self):
        """Validate event data"""
        if self.date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past")
        
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

    @property
    def approved_volunteers_count(self):
        return self.participations.filter(status='APPROVED').count()

    @property
    def is_full(self):
        return self.approved_volunteers_count >= self.capacity

    @property
    def available_spots(self):
        return max(0, self.capacity - self.approved_volunteers_count)

    @property
    def is_joinable(self):
        """Event can be joined if approved, not full, and not past date"""
        return (self.status == 'APPROVED' and 
                not self.is_full and 
                self.date >= timezone.now().date())

    @property
    def is_upcoming(self):
        return self.date >= timezone.now().date()

    def has_user_participation(self, user):
        return self.participations.filter(user=user).exists()

    def get_user_participation_status(self, user):
        try:
            participation = self.participations.get(user=user)
            return participation.status
        except VolunteerParticipation.DoesNotExist:
            return None

    def can_user_manage(self, user):
        """Check if user can manage this event"""
        if user.role == 'admin':
            return True
        if user.role == 'leader' and self.village.leader == user:
            return True
        if self.organizer == user:
            return True
        return False

    def __str__(self):
        return f"{self.title} - {self.village.village} ({self.status})"


class VolunteerParticipation(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending Approval"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    participation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_participations")
    event = models.ForeignKey(VolunteeringEvent, on_delete=models.CASCADE, related_name="participations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-joined_at']
        verbose_name = "Volunteer Participation"
        verbose_name_plural = "Volunteer Participations"

    def clean(self):
        """Validate participation"""
        if self.event.status != 'APPROVED':
            raise ValidationError("Cannot participate in unapproved events")
        
        if self.event.is_full and self.status != 'APPROVED':
            raise ValidationError("Event is full")

    def __str__(self):
        return f"{self.user} - {self.event} ({self.status})"