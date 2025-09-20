from django.db import models
from django.conf import settings
import uuid
from django.core.exceptions import ValidationError



class Location(models.Model):
    village_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    sector = models.CharField(max_length=50)
    cell = models.CharField(max_length=50)
    village = models.CharField(max_length=50)
    leader = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='led_villages',
        default="5aa97242-7ac2-4096-9a78-2b6c21abef62" 
    )
    class Meta:
        db_table = 'Location_location'

    def get_full_address(self):
        return f"{self.village}, {self.cell}, {self.sector}, {self.district}, {self.province}"
    
    def __str__(self):
        return self.get_full_address()
    
    def clean(self):
        """Ensure a user is leader of only one village."""
        if self.leader:
            # Check if this user is already a leader of another village
            existing = Village.objects.filter(leader=self.leader).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(f"{self.leader} is already the leader of another village.")
    
