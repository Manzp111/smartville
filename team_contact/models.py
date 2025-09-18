from django.db import models
from django.conf import settings

class TeamMember(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    tagline = models.TextField(blank=True)
    degree = models.CharField(max_length=255, blank=True)
    university = models.CharField(max_length=255, blank=True)
    bio = models.TextField()
    photo_url = models.URLField(max_length=500, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    linkedin = models.URLField(max_length=500, blank=True)
    github = models.URLField(max_length=500, blank=True)
    website = models.URLField(max_length=500, blank=True)
    twitter = models.URLField(max_length=500, blank=True)
    location = models.CharField(max_length=255, blank=True)
    skills = models.JSONField(default=list, blank=True)  # [{name, icon?}]
    certifications = models.JSONField(default=list, blank=True)  # ["AWS Certified Developer", ...]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    INQUIRY_TYPES = [
        ('general', 'General'),
        ('implementation', 'Implementation'),
        ('partnership', 'Partnership'),
        ('technical', 'Technical'),
        ('demo', 'Demo'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    inquiry_type = models.CharField(max_length=32, choices=INQUIRY_TYPES)
    message = models.TextField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.inquiry_type})"

class ContactReply(models.Model):
    message = models.ForeignKey(ContactMessage, related_name='replies', on_delete=models.CASCADE)
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reply_message = models.TextField()
    replied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to {self.message.id} by {self.replied_by}"