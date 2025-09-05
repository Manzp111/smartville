from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from account.models import User, Person, Location, OTP
from account.utils import generate_otp
from datetime import timedelta
from django.utils import timezone

class RegisterViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('register')  # URL from your urls.py

    def test_register_user_success(self):
        data = {
            "email": "test@example.com",
            "password": "StrongPass1!",
            "confirm_password": "StrongPass1!",
            "person": {
                "national_id": 1234567890123456,
                "location": {
                    "province": "Kigali",
                    "district": "Gasabo",
                    "sector": "Kacyiru",
                    "cell": "Kimironko",
                    "village": "Village1"
                }
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertIn("message", response.data)

    def test_register_user_password_mismatch(self):
        data = {
            "email": "test2@example.com",
            "password": "StrongPass1!",
            "confirm_password": "WrongPass1!",
            "person": {
                "national_id": 1234567890123457,
                "location": {
                    "province": "Kigali",
                    "district": "Gasabo",
                    "sector": "Kacyiru",
                    "cell": "Kimironko",
                    "village": "Village2"
                }
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwords do not match.", str(response.data))

    def test_register_user_existing_email(self):
        # Pre-create user
        location = Location.objects.create(
            province="Kigali", district="Gasabo", sector="Kacyiru", cell="Kimironko", village="VillageX"
        )
        person = Person.objects.create(national_id=1234567890123458, location=location)
        User.objects.create_user(email="existing@example.com", password="StrongPass1!", person=person)

        data = {
            "email": "existing@example.com",
            "password": "StrongPass1!",
            "confirm_password": "StrongPass1!",
            "person": {
                "national_id": 1234567890123459,
                "location": {
                    "province": "Kigali",
                    "district": "Gasabo",
                    "sector": "Kacyiru",
                    "cell": "Kimironko",
                    "village": "VillageY"
                }
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check the correct field key
        self.assertIn("Email exist", str(response.data['email']))


class OTPVerifyViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('verify-otp')
        # Create location, person, and user
        self.location = Location.objects.create(
            province="Kigali", district="Gasabo", sector="Kacyiru", cell="Kimironko", village="Village1"
        )
        self.person = Person.objects.create(national_id=1234567890123456, location=self.location)
        self.user = User.objects.create_user(email="otpuser@example.com", password="StrongPass1!", person=self.person)
        self.otp = generate_otp(self.user, purpose="verification")

    def test_verify_otp_success(self):
        data = {"email": self.user.email, "otp_code": self.otp.code}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.otp.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertTrue(self.otp.is_used)

    def test_verify_otp_invalid_code(self):
        # OTP code must be <= 6 characters
        data = {"email": self.user.email, "otp_code": "000000"}  
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check non_field_errors
        self.assertIn("Invalid or expired OTP", str(response.data['non_field_errors']))

    def test_verify_otp_expired(self):
        # Expire OTP manually
        self.otp.created_at = timezone.now() - timedelta(hours=1)
        self.otp.save()
        data = {"email": self.user.email, "otp_code": self.otp.code}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("OTP expired", str(response.data['non_field_errors']))
