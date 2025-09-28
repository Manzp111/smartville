# accounts/tests/test_auth.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User

class AuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")
        self.verify_url = reverse("verify-otp")
        self.resend_url = reverse("resend-otp")
        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.me_url = reverse("user_profile")

    def test_register_user(self):
        payload = {
            "phone_number": "0788000000",
            "password": "Test1234@",
            "confirm_password": "Test1234@",
            "person": {
                "first_name": "John",
                "last_name": "Doe",
                "national_id": "1234567890123456",
                "gender": "male"
            },
            "location_id": "f138c017-e26d-418b-85c6-b2978e348e91"
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(phone_number="0788000000").exists())

    def test_login_unverified_user(self):
        user = User.objects.create_user(
            phone_number="0788111111",
            password="Test1234@",
            is_verified=False
        )
        response = self.client.post(self.login_url, {
            "phone_number": "0788111111",
            "password": "Test1234@"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data.get("status", "").lower())

    def test_login_verified_user_and_access_profile(self):
        user = User.objects.create_user(
            phone_number="0788222222",
            password="Test1234@",
            is_verified=True
        )
        # Login
        response = self.client.post(self.login_url, {
            "phone_number": "0788222222",
            "password": "Test1234@"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access = response.data["data"]["access"]

        # Authenticated profile
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me_response = self.client.get(self.me_url)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["data"]["phone_number"], "0788222222")

    def test_refresh_token(self):
        user = User.objects.create_user(
            phone_number="0788333333",
            password="Test1234@",
            is_verified=True
        )
        login = self.client.post(self.login_url, {
            "phone_number": "0788333333",
            "password": "Test1234@"
        })
        refresh = login.data["data"]["refresh"]

        response = self.client.post(self.refresh_url, {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["data"])
