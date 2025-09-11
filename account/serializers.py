# accounts/serializers.py
from rest_framework import serializers
from .models import User, Person, OTP
from rest_framework.validators import UniqueValidator
from django.db import transaction
from .utils import generate_otp
from .tasks import send_verification_email_task
from django.utils import timezone
from pytz import timezone as pytz_timezone


# -----------------------------
# Person Serializer
# -----------------------------
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["first_name", "last_name", "phone_number"]


# -----------------------------
# Register Serializer
# -----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email already exists.")]
    )

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password", "person"]

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
        email = self.initial_data.get("email", "")
        if value == email:
            raise serializers.ValidationError("Password must not be the same as email.")
        return value

    # Confirm password match
    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        person_data = validated_data.pop("person")
        validated_data.pop("confirm_password")

        with transaction.atomic():
            person = Person.objects.create(**person_data)
            user = User.objects.create(
                email=validated_data["email"],
                person=person,
                is_active=True,
                is_verified=False
            )
            user.set_password(validated_data["password"])
            user.save()

            otp = generate_otp(user, purpose="verification")
            send_verification_email_task.delay(
                user.person.first_name,
                user.person.last_name,
                user.email,
                otp.code
            )

        return user


# -----------------------------
# User List Serializer
# -----------------------------
class UserListSerializer(serializers.ModelSerializer):
    person = PersonSerializer()

    class Meta:
        model = User
        fields = ["user_id", "email", "role", "is_verified", "is_active", "person", "created_at"]


# -----------------------------
# OTP Verify Serializer
# -----------------------------
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
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
            user = User.objects.get(email=data['email'])
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
            "data": {"email": user.email}
        }


# -----------------------------
# Resend OTP Serializer
# -----------------------------
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email.")

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
            user.email,
            otp.code
        )

        return {
            "success": True,
            "message": "A new OTP has been sent to your email.",
            "data": {"email": user.email}
        }
