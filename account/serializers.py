# accounts/serializers.py
from rest_framework import serializers
from .models import User, Person, OTP
from rest_framework.validators import UniqueValidator
from django.db import transaction
from .utils import generate_otp
from .tasks import send_verification_email_task
from django.utils import timezone
from pytz import timezone as pytz_timezone
from event.utils import success_response, error_response
from Location.models import Location
from Resident.models import Resident

# -----------------------------
# Person Serializer
# -----------------------------
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["first_name", "last_name", "phone_number", "national_id", "gender", "person_type"]


# -----------------------------
# Register Serializer
# -----------------------------
class RegisterSerializer(serializers.ModelSerializer):

    person = PersonSerializer()
    password = serializers.CharField(write_only=True, min_length=8)
    location_id = serializers.UUIDField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Phone number already exists.")]
    )

    class Meta:
        model = User
        fields = ["password", "confirm_password", "person", "phone_number","location_id"]

    # Password validation
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        if ' ' in value:
            raise serializers.ValidationError("Password must not contain spaces.")
        if value.islower() or value.isupper():
            raise serializers.ValidationError("Password must contain both uppercase and lowercase letters.")
        
        phone_number = self.initial_data.get("phone_number", "")
        if value == phone_number:
            raise serializers.ValidationError("Password must not be the same as phone number.")
        return value

    # Confirm password match
    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    # Create user
    def create(self, validated_data):
        person_data = validated_data.pop("person")
        location_id = validated_data.pop("location_id")
        validated_data.pop("confirm_password")
        phone_number = validated_data.pop("phone_number")

        with transaction.atomic():
            # Create Person
            person_data["phone_number"] = phone_number
            person = Person.objects.create(
                phone_number=validated_data["phone_number"], 
                **person_data)

            # Create User
            user = User.objects.create(
                phone_number=phone_number,
                person=person,
                is_active=True,
                is_verified=False
            )
            user.set_password(validated_data["password"])
            user.save()

            location = Location.objects.get(village_id=location_id)
            Resident.objects.create(
                person=person,
                location=location,
                added_by=user,  # optional, user created their own resident
                status="PENDING",
            )

            # Generate OTP
            # otp = generate_otp(user, purpose="verification")
            # send_verification_email_task.delay(
            #     user.person.first_name,
            #     user.person.last_name,
            #     user.phone_number,  
            #     otp.code
            # )

        return user


# -----------------------------
# User List Serializer
# -----------------------------
class UserListSerializer(serializers.ModelSerializer):
    person = PersonSerializer()

    class Meta:
        model = User
        fields = ["user_id", "phone_number", "role", "is_verified", "is_active", "person", "created_at"]


# -----------------------------
# OTP Verify Serializer
# -----------------------------
class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp_code = serializers.CharField(
        min_length=6,
        max_length=6,
        error_messages={
            "max_length": "OTP must be exactly 6 digits.",
            "min_length": "OTP must be exactly 6 digits."
        }
    )

    def validate(self, data):
        try:
            user = User.objects.get(phone_number=data['phone_number'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        try:
            otp = OTP.objects.filter(user=user, code=data['otp_code'], is_used=False).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP.")

        if otp.is_expired():
            raise serializers.ValidationError("OTP expired.")

        data['user'] = user
        data['otp'] = otp
        return data

    def save(self, **kwargs):
        user = self.validated_data['user']
        otp = self.validated_data['otp']

        user.is_verified = True
        user.save()

        otp.is_used = True
        otp.save()

        return {
            "success": True,
            "message": "User successfully verified.",
            "data": {"phone_number": user.phone_number}
        }


# -----------------------------
# Resend OTP Serializer
# -----------------------------
class ResendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        try:
            user = User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this phone number.")

        if user.is_verified:
            raise serializers.ValidationError("User is already verified.")

        self.user = user
        return value

    def save(self, **kwargs):
        user = self.user
        last_otp = OTP.objects.filter(user=user, purpose="verification", is_used=False).order_by("-created_at").first()

        now = timezone.now().astimezone(pytz_timezone('Africa/Kigali'))
        if last_otp and (now - last_otp.created_at).total_seconds() < 120:
            raise serializers.ValidationError("Please wait a few minutes before requesting another OTP.")

        if last_otp:
            last_otp.is_used = True
            last_otp.save()

        otp = generate_otp(user, purpose="verification")
        send_verification_email_task.delay(
            user.person.first_name,
            user.person.last_name,
            user.phone_number,  # send OTP to phone number
            otp.code
        )

        return {
            "success": True,
            "message": f"A new OTP has been sent to your {user.phone_number}",
            "data": {"phone_number": user.phone_number}
        }
