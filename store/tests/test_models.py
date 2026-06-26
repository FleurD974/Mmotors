from django.test import TestCase
from django.urls import reverse

from accounts.models import Customer
from store.models import Application, Car

class CarTest(TestCase):
    def setUp(self):
        self.car = Car.objects.create(
            brand= 'Test',
            model='first',
            engine='essence',
            leasing_price=100,
            registration_number='AA-111-AA',
        )

    def test_car_slug_is_automaticcaly_generated(self):
        self.assertEqual(self.car.slug, 'aa-111-aa')

    def test_car_absolute_url(self):
        self.assertEqual(
            self.car.get_absolute_url(),
            reverse('car', kwargs={"slug": self.car.slug})
        )
        
class ApplicationTest(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            email='fleur@test.com',
            first_name='fleur',
            last_name='Test',
            password='test123',
        )
        self.user_staff = Customer.objects.create_user(
            email='admin@test.com',
            first_name='Admin',
            last_name='Doe',
            password='test456',
            is_staff=True,
        )
        self.car = Car.objects.create(
            brand= 'Test',
            model='first',
            engine='essence',
            leasing_price=100,
            registration_number='AA-111-AA',
        )
        self.application = Application.objects.create(
            customer=self.user,
            car=self.car,
            status='draft'
        )

    def test_application_approve_method(self):
        self.application.status = 'submitted'
        self.application.save()

        self.application.approve()

        self.application.refresh_from_db()
        self.car.refresh_from_db()

        self.assertEqual(self.application.status, 'approved')
        self.assertIsNotNone(self.application.reviewed_at)
        self.assertFalse(self.car.is_available)

    def test_application_reject_method(self):
        self.application.status = 'submitted'
        self.application.save()

        self.application.reject()

        self.application.refresh_from_db()
        self.car.refresh_from_db()

        self.assertEqual(self.application.status, 'rejected')
        self.assertIsNotNone(self.application.reviewed_at)
        self.assertTrue(self.car.is_available)
