from django.db import models
from Village.models import Village
import uuid
from django.conf import settings


CATEGORY_CHOICES = [
        ("emergency", "Emergency"),
        ("health", "Health"),
        ("leadership", "Leadership"),
        ("utilities", "Utilities"),
]



class Contact(models.Model):
    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]
    contact_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20 ,null=True, blank=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    description = models.TextField(blank=True, null=True)
    village = models.OneToOneField(Village, blank=True, null=True,on_delete=models.CASCADE, related_name="contact")
    hours = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
         settings.AUTH_USER_MODEL,
         on_delete=models.CASCADE,
         related_name="created_contacts"
     )

    def __str__(self):
        return f"{self.name} ({self.category})"












# # contacts/models.py
# import uuid
# from django.db import models
# from django.conf import settings
# from Village.models import Village

# class Contact(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100)
#     phone_number = models.CharField(max_length=15, unique=True)
#     role = models.CharField(max_length=50)  # e.g. leader, security, health worker
#     village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True, blank=True, related_name="contacts")
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="created_contacts"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} ({self.role})"
