from django.urls import reverse
from rest_framework.test import APITestCase
from account.models import User, Person
from Location.models import Location
from complaint.models import Complaint

class ComplaintAPITest(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(village="Village A")
        self.person = Person.objects.create(first_name="John", location=self.location)
        self.user = User.objects.create_user(email="john@example.com", password="pass", person=self.person)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('complaint-list')  # router basename

    def test_create_complaint_auto_assigns_location(self):
        data = {
            "description": "Water shortage in my area",
            "is_anonymous": False
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        complaint = Complaint.objects.get(description="Water shortage in my area")
        self.assertEqual(complaint.location, self.location)
        self.assertEqual(complaint.complainant, self.person)

    def test_list_complaints(self):
        Complaint.objects.create(
            complainant=self.person,
            description="Test complaint",
            location=self.location
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['data']) >= 1)