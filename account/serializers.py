from rest_framework import serializers
from .models import User, Person, Location, OTP
import uuid
from .utils import generate_otp
from rest_framework.validators import UniqueValidator

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["province", "district", "sector", "cell", "village"]


class PersonSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = Person
        fields = ["national_id", "location"] 

    def validate_national_id(self, value):
        if not str(value).isdigit() or len(str(value)) != 16:
            raise serializers.ValidationError("National ID must be exactly 16 digits.")
        return value

class RegisterSerializer(serializers.ModelSerializer):
    person = PersonSerializer()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email exist.")]
    )

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password", "person"]
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
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
        if value in ['password', '12345678', 'qwertyui', 'letmein', 'welcome']:
            raise serializers.ValidationError("Password is too common.")
        # Check if password is same as email
        email = self.initial_data.get("email", "")
        if value == email:
            raise serializers.ValidationError("Password must not be the same as email.")
        

        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email exist.")
        return value
    

    def create(self, validated_data):
        # Extract person and location data
        validated_data.pop("confirm_password")
        person_data = validated_data.pop("person")
        location_data = person_data.pop("location")

        # Ensure location exists or create
        location, _ = Location.objects.get_or_create(**location_data)

        # Create person
        person = Person.objects.create(location=location, **person_data)

        # Create user
        user = User.objects.create(
            email=validated_data["email"],
            person=person,
            is_active=True,
            is_verified=False
        )
        user.set_password(validated_data["password"])
        user.save()

        
        return user
    



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
            raise serializers.ValidationError("User not found")

        try:
            otp = OTP.objects.filter(user=user, code=data['otp_code'], is_used=False).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP")

        if otp.is_expired():
            raise serializers.ValidationError("OTP expired")

        data['user'] = user
        data['otp'] = otp
        return data

    def save(self, **kwargs):
        user = self.validated_data['user']
        otp = self.validated_data['otp']

        # Mark user as verified
        user.is_verified = True
        user.save()

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        return user



