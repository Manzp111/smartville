from django.test import TestCase
from account.models import User, Person, Location

class UserModelTest(TestCase):

    def setUp(self):
        # Create a location
        self.location = Location.objects.create(
            province="Kigali",
            district="Gasabo",
            sector="Kacyiru",
            cell="Kacyiru",
            village="Village1"
        )

        # Create a person
        self.person = Person.objects.create(
            national_id=123456789,
            first_name="John",
            last_name="Doe",
            location=self.location,
            date_of_birth="1990-01-01",
            gender="male",
            person_type="resident",
            phone_number="0781234567"
        )

    def test_create_normal_user_with_person(self):
        user = User.objects.create_user(
            email="user@test.com",
            password="password123",
            person=self.person,
            username="johndoe"
        )
        self.assertEqual(user.email, "user@test.com")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.person, self.person)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_normal_user_without_person_should_fail(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="noperson@test.com",
                password="password123",
                username="noperson"
            )

    def test_create_superuser_without_person(self):
        superuser = User.objects.create_superuser(
            email="admin@test.com",
            password="admin123"
        )
        self.assertEqual(superuser.email, "admin@test.com")
        self.assertTrue(superuser.check_password("admin123"))
        self.assertIsNone(superuser.person)  # Superuser has no person
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_str_method_normal_user(self):
        user = User.objects.create_user(
            email="struser@test.com",
            password="password123",
            person=self.person,
            username="struser"
        )
        self.assertEqual(str(user), f"{self.person.first_name}-{self.person.location.village}_{user.role}")

    def test_str_method_superuser_without_person(self):
        superuser = User.objects.create_superuser(
            email="superstr@test.com",
            password="superpassword"
        )
        self.assertEqual(str(superuser), f"{superuser.email}_{superuser.role}")
