from django.test import TestCase

from accounts.models import Customer
from store.models import Car

class CustomerTest(TestCase):
    def setUp(self):
        Car.objects.create(
            brand= 'Test',
            model='first',
            engine='essence',
            leasing_price=100,
            registration_number='AA-111-AA',
        )
        self.user = Customer.objects.create_user(
            email='test@test.com',
            password='test123'
        )

    def test_create_application(self):
        # verifier quon a le httprepsonse?
        self.user.create_application(slug='aa-111-aa')
        self.assertEqual(self.user.application.status, 'draft')
        self.assertEqual(self.user.application.car.slug, 'aa-111-aa')
