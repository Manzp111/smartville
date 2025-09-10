import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import pytz
from datetime import timedelta


GENDER_CHOICES = [
    ('male', 'MALE'),
    ('female', 'FEMALE')
]

PERSON_TYPE_CHOICES = [
    ('resident', 'RESIDENT'),
    ('visitor', 'VISITOR')
]

class Person(models.Model):
    person_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    national_id = models.BigIntegerField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    location = models.ForeignKey("Location.Location", on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    person_type = models.CharField(max_length=10, choices=PERSON_TYPE_CHOICES, default='resident')
    registration_date = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else str(self.person_id)


# -----------------------------
# User Manager
# -----------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        # Optionally create a Person linked to user
        if first_name or last_name:
            from account.models import Person
            person = Person.objects.create(
                first_name=first_name,
                last_name=last_name,
                person_type='resident'
            )
            user.person = person
            user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email=email, password=password, **extra_fields)



ROLE_CHOICES = [
    ('resident', 'RESIDENT'),
    ('leader', 'LEADER'),
    ('admin', 'ADMIN')
]

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        if self.person:
            return f"{self.person.first_name}-{self.person.last_name}_{self.role}"
        return f"{self.email}_{self.role}"



class OTP(models.Model):
    def get_kigali_time():
        return timezone.now().astimezone(pytz.timezone('Africa/Kigali'))
    PURPOSE_CHOICES = [
        ('verification', 'Verification'),
        ('reset', 'Password Reset')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=100, unique=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(default=get_kigali_time)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        now = timezone.now().astimezone(pytz.timezone('Africa/Kigali'))
        return now > self.created_at + timedelta(minutes=30)

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.code}"
