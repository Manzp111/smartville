from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

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
    national_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    person_type = models.CharField(max_length=10, choices=PERSON_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True)
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}-{self.location.village}"



class UserManager(BaseUserManager):

    def validate_user(self, email, password):
        if not email:
            raise TypeError('Users should have Email')
        if not password:
            raise TypeError('Users should have Password')

    def create_user(self, email, password=None, person=None, **extra_fields):
        self.validate_user(email=email, password=password)

        # Normal users must have a person, superusers can skip it
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



ROLE = [
    ('resident', 'RESIDENT'),
    ('leader', 'LEADER'),
    ('admin', 'ADMIN')
]

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, null=True, blank=True)  # <- optional now
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified= models.BooleanField(default=False)
    username = models.CharField(max_length=255)
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
