from django.test import TestCase

from store.forms import CarForm


class CarFormTest(TestCase):
    def test_car_cannot_be_purchased_and_leased(self):
        form = CarForm(data={
            'brand': 'Renault',
            'model': 'Clio',
            'engine': 'Essence',
            'mileage': 10000,
            'passenger_number': 5,
            'is_purchased': True,
            'is_leased': True,
            'purchase_price': 10000,
            'leasing_price': 250,
            'registration_number': 'AA-123-AA',
            'description': 'Description'
        })

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Une voiture ne peut pas être en location et à l\'achat.',
            form.non_field_errors()
        )

    def test_car_must_be_purchased_or_leased(self):
        form = CarForm(data={
            'brand': 'Renault',
            'model': 'Clio',
            'engine': 'Essence',
            'mileage': 10000,
            'passenger_number': 5,
            'is_purchased': False,
            'is_leased': False,
            'purchase_price': 10000,
            'leasing_price': 250,
            'registration_number': 'AA-123-AA',
            'description': 'Description'
        })

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Une voiture doit être en location ou à l\'achat.',
            form.non_field_errors()
        )

    def test_valid_form(self):
        form = CarForm(data={
            'brand': 'Renault',
            'model': 'Clio',
            'engine': 'Essence',
            'mileage': 10000,
            'passenger_number': 5,
            'is_purchased': False,
            'is_leased': True,
            'purchase_price': 10000,
            'leasing_price': 250,
            'registration_number': 'AA-123-AA',
            'description': 'Description'
        })

        self.assertTrue(form.is_valid())
