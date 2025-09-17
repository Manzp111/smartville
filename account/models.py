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
    def normalize_phone(self,phone):
        """
        Normalize Rwandan phone numbers to format: 250XXXXXXXXX
        Examples:
            0781234567 -> 250781234567
            +250781234567 -> 250781234567
            250781234567 -> 250781234567
        """
        if not phone:
            return None

        
        phone = phone.replace(" ", "").replace("-", "").replace("+", "")

        
        if phone.startswith("0"):
            phone = "250" + phone[1:]

        return phone


    def create_user(self, phone_number, password=None, first_name=None, last_name=None, national_id=None,gender=None,person_type='resident',**extra_fields):
        if not phone_number:
            raise ValueError("phone_number is required")
        if not password:
            raise ValueError("Password is required")

        phone_number = self.normalize_phone(phone_number)

        person = Person.objects.create(
            first_name=first_name,
            last_name=last_name,
            national_id=national_id,
            phone_number=phone_number,
            gender=gender,
            person_type=person_type
        )


        user = self.model(phone_number=phone_number, person=person, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(phone_number=phone_number, password=password, **extra_fields)
        if not user.person:
            from account.models import Person
            person = Person.objects.create(
                phone_number=user.phone_number,
                person_type='resident'
            )
            user.person = person
            user.save()

        return user
    def delete(self, *args, **kwargs):
        # Delete related person first
        if self.person:
            self.person.delete()
        super().delete(*args, **kwargs)



ROLE_CHOICES = [
    ('resident', 'RESIDENT'),
    ('leader', 'LEADER'),
    ('admin', 'ADMIN')
]

class User(AbstractBaseUser, PermissionsMixin):
    # user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'
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
            return f"{self.user_id}-{self.person.first_name}-{self.person.last_name}_{self.role}"
        return f"{self.phone_number}_{self.role}"
    
    def save(self, *args, **kwargs):
        # Update Person phone number whenever User phone_number changes
        if self.person and self.phone_number != self.person.phone_number:
            self.person.phone_number = self.phone_number
            self.person.save()
        super().save(*args, **kwargs)



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
    
    def is_valid(self):
        return not self.is_expired() and not self.is_used

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.code}"
