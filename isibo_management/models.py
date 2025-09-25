import uuid
from django.db import models
from account.models import User
from Village.models import Village

class Isibo(models.Model):
    isibo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name="isibos")
    leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="isibos_led"
    )
    created_by = models.ForeignKey(
        User,  # village leader who created it
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="isibos_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.village.village})"
