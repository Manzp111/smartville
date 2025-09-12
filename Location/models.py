from django.db import models
from django.conf import settings
import uuid


class Location(models.Model):
    village_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    sector = models.CharField(max_length=50)
    cell = models.CharField(max_length=50)
    village = models.CharField(max_length=50)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='led_villages',
        default="dc558906-6538-43ec-a6e7-4e877421ae64" 
    )

    def get_full_address(self):
        return f"{self.village}, {self.cell}, {self.sector}, {self.district}, {self.province}"
    
    def __str__(self):
        return self.get_full_address()
    
    @property
    def resident_count(self):
        return self.residents.filter(is_deleted=False).count()