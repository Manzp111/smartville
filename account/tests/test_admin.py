# accounts/tests/test_admin_users.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from account.models import User

class AdminUserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            phone_number="0788444444",
            password="Admin1234@",
            is_verified=True
        )
        # Authenticate as admin
        login = self.client.post(reverse("token_obtain_pair"), {
            "phone_number": "0788444444",
            "password": "Admin1234@"
        })
        token = login.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_admin_can_list_users(self):
        url = reverse("admin-users-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_user(self):
        url = reverse("admin-users-list")
        payload = {
            "phone_number": "0788555555",
            "password": "User1234@",
            "confirm_password": "User1234@",
            "role": "resident",
            "person": {
                "first_name": "Jane",
                "last_name": "Smith"
            }
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
