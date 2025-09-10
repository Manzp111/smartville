from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.utils import timezone
from datetime import timedelta
import pytz

# -----------------------------
# Location Model
# -----------------------------
class Location(models.Model):
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    sector = models.CharField(max_length=50)
    cell = models.CharField(max_length=50)
    village = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.village}, {self.sector}, {self.district}, {self.province}"


# -----------------------------
# Person Model
# -----------------------------
GENDER_CHOICES = [
    ('male', 'MALE'),
    ('female', 'FEMALE')
]

PERSON_TYPE_CHOICES = [
    ('visitor', 'VISITOR'),
    ('resident', 'RESIDENT')
]

class Person(models.Model):
    person_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    national_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    person_type = models.CharField(max_length=10, choices=PERSON_TYPE_CHOICES, default='resident')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} - {self.location.village}"
        return f"{self.person_id} - {self.location.village}"


# -----------------------------
# Custom User Manager
# -----------------------------
class UserManager(BaseUserManager):
    def validate_user(self, email, password):
        if not email:
            raise TypeError('Users should have Email')
        if not password:
            raise TypeError('Users should have Password')

    def create_user(self, email, password=None, person=None, **extra_fields):
        self.validate_user(email=email, password=password)
        if person is None and not extra_fields.get('is_superuser', False):
            raise ValueError("Normal users must have a linked person")
        user = self.model(
            email=self.normalize_email(email),
            person=person,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, person=None, **extra_fields)


# -----------------------------
# User Model
# -----------------------------
ROLE = [
    ('resident', 'RESIDENT'),
    ('leader', 'LEADER'),
    ('admin', 'ADMIN')
]

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    username = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, choices=ROLE, default='resident')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects = UserManager()

    def __str__(self):
        if self.person:
            return f"{self.person.first_name}-{self.person.location.village}_{self.role}"
        return f"{self.email}_{self.role}"


# -----------------------------
# OTP Model
# -----------------------------
class OTP(models.Model):
    PURPOSE_CHOICES = [
        ("verification", "Verification"),
        ("reset", "Password Reset"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=100, unique=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    def get_kigali_time():
        return timezone.now().astimezone(pytz.timezone('Africa/Kigali'))

    created_at = models.DateTimeField(default=get_kigali_time)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        now = timezone.now().astimezone(pytz.timezone('Africa/Kigali'))
        return now > self.created_at + timedelta(minutes=30)

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.code}"
