from django.urls import reverse
from rest_framework.test import APITestCase
from account.models import User, Person
from Location.models import Location
from alert.models import CommunityAlert

class CommunityAlertAPITest(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(name="Village B")
        self.person = Person.objects.create(first_name="Alice", location=self.location)
        self.user = User.objects.create_user(email="alice@example.com", password="pass", person=self.person)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('alert-list')  # router basename

    def test_create_alert_auto_assigns_location(self):
        data = {
            "title": "Flood warning",
            "description": "River is rising fast",
            "alert_type": "Weather",
            "urgency_level": "High",
            "specific_location": "Near bridge",
            "incident_date": "2025-09-12",
            "incident_time": "14:00:00",
            "allow_sharing": True,
            "contact_phone": "0781234567",
            "is_anonymous": False
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        alert = CommunityAlert.objects.get(title="Flood warning")
        self.assertEqual(alert.location, self.location)
        self.assertEqual(alert.reporter, self.person)

    def test_list_alerts(self):
        CommunityAlert.objects.create(
            reporter=self.person,
            title="Test Alert",
            description="Test",
            alert_type="General",
            urgency_level="Low",
            location=self.location,
            incident_date="2025-09-12",
            incident_time="14:00:00"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['data']) >= 1)