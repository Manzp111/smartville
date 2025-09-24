
# contacts/models.py
import uuid
from django.db import models
from django.conf import settings
from Village.models import Village

class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=50)  # e.g. leader, security, health worker
    village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True, blank=True, related_name="contacts")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_contacts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
