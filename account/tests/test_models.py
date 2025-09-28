from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from account.models import User, Person, OTP


class PersonModelTest(TestCase):
    def test_soft_delete_and_restore(self):
        person = Person.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="0781234567",
            gender="male"
        )

        # Initially not deleted
        self.assertFalse(person.is_deleted)

        # Soft delete
        person.soft_delete()
        self.assertTrue(person.is_deleted)
        self.assertIsNotNone(person.deleted_at)

        # Restore
        person.restore()
        self.assertFalse(person.is_deleted)
        self.assertIsNone(person.deleted_at)


class UserManagerTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            phone_number="0781234567",
            password="password123",
            first_name="Alice",
            last_name="Smith",
            gender="female"
        )

        self.assertEqual(user.phone_number, "250781234567")  # normalized
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.person.first_name, "Alice")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            phone_number="0788765432",
            password="adminpass"
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_active)


class UserModelTest(TestCase):
    def test_soft_delete_and_restore(self):
        user = User.objects.create_user(
            phone_number="0781234567",
            password="testpass"
        )

        # Soft delete
        self.assertFalse(user.is_deleted)
        user.soft_delete()
        self.assertTrue(user.is_deleted)
        self.assertIsNotNone(user.deleted_at)

        # Restore
        user.restore()
        self.assertFalse(user.is_deleted)
        self.assertIsNone(user.deleted_at)

    def test_user_person_phone_sync(self):
        user = User.objects.create_user(
            phone_number="0781234567",
            password="syncpass"
        )

        # Update user phone
        user.phone_number = "0780000000"
        user.save()

        # Person phone must match normalized phone
        user.refresh_from_db()
        self.assertEqual(user.person.phone_number, "250780000000")


class OTPModelTest(TestCase):
    def test_otp_validity_and_expiry(self):
        user = User.objects.create_user(
            phone_number="0781234567",
            password="otppass"
        )

        otp = OTP.objects.create(
            user=user,
            code="123456",
            purpose="verification"
        )

        self.assertTrue(otp.is_valid())
        self.assertFalse(otp.is_expired())

        # Simulate expiry
        otp.created_at = timezone.now() - timedelta(minutes=31)
        otp.save()
        self.assertTrue(otp.is_expired())
        self.assertFalse(otp.is_valid())

    def test_used_otp_is_invalid(self):
        user = User.objects.create_user(
            phone_number="0781234567",
            password="otppass"
        )

        otp = OTP.objects.create(
            user=user,
            code="654321",
            purpose="reset"
        )

        otp.is_used = True
        otp.save()

        self.assertFalse(otp.is_valid())
