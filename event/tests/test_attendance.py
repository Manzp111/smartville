from django.urls import reverse
from rest_framework.test import APITestCase
from account.models import User, Person
from Location.models import Location
from event.models import Event



class EventTests(APITestCase):

    def setUp(self):
        self.location = Location.objects.create(name="Village A")
        self.person = Person.objects.create(first_name="John", location=self.location)
        self.user = User.objects.create_user(email="john@example.com", password="pass", person=self.person)
        self.client.forcce_authenticate(user=self.user)

    def test_create_event_assigns_village(self):
        url = reverse('event-list')  # or your router name
        data = {
            "title": "Umuganda",
            "description": "Community work",
            "location": "Village A",
            "date": "2025-09-12",
            "start_time": "09:00:00",
            "end_time": "17:00:00"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        event = Event.objects.get(title="Umuganda")
        self.assertEqual(event.village, self.location)