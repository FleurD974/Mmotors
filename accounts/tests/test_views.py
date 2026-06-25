from django.test import TestCase
from django.urls import reverse

from accounts.models import Customer

class StoreLoggedInTest(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            email="fleur@test.com",
            first_name="fleur",
            last_name="Test",
            password="test123",
        )

    def test_valid_login(self):
        data = {'email': 'fleur@test.com', 'password': 'test123'}
        response = self.client.post(reverse('login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.client.login(email='fleur@test.com', password='test123')
        response = self.client.get(reverse('index'))
        self.assertIn('Profil', str(response.content))

    def test_invalid_login(self):
        data = {'email': 'fleur@test.com', 'password': 'test'}
        response = self.client.post(reverse('login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_profile_change(self):
        self.client.login(email='fleur@test.com', password='test123')
        data = {
            'email': 'fleur@test.com',
            'password': 'test123',
            'first_name': 'fleur',
            'last_name': 'Smith',
        }

        response = self.client.post(reverse('profile'), data=data)
        self.assertEqual(response.status_code, 302)
        user_infos = Customer.objects.get(email='fleur@test.com')
        self.assertEqual(user_infos.last_name, 'Smith')

    def test_profile_do_not_change_if_incorrect_password(self):
        self.client.login(email='fleur@test.com', password='test123')
        data = {
            'email': 'fleur@test.com',
            'password': 'test13',
            'first_name': 'fleur',
            'last_name': 'Smith',
        }
        response = self.client.post(reverse('profile'), data=data, follow=True)
        self.assertContains(response, "Le mot de passe est invalide.")
        user = Customer.objects.get(email='fleur@test.com')
        self.assertEqual(user.last_name, 'Test')

    def test_profile_with_get(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(reverse('profile'))

        form = response.context['form']

        self.assertEqual(form.initial['first_name'], 'fleur')
        self.assertEqual(form.initial['last_name'], 'Test')
        self.assertIn('form', response.context)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse('login')}?next={reverse('profile')}'
        )

    def test_signup_get(self):
        response = self.client.get(reverse('signup'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_signup_create_user_and_authenticate_customer(self):
        data = {
            'email': 'aurore@test.com',
            'first_name': 'Aurore',
            'last_name': 'Dupont',
            'password': 'test1234',
        }
        response = self.client.post(reverse('signup'), data=data)

        self.assertRedirects(response, reverse('index'))
        self.assertTrue(Customer.objects.filter(email='aurore@test.com').exists())
        self.assertIn('_auth_user_id', self.client.session)

        user = Customer.objects.get(email='aurore@test.com')

        self.assertEqual(user.first_name, 'Aurore')
        self.assertEqual(user.last_name, 'Dupont')

    def test_signup_password_is_hashed(self):
        data = {
            'email': 'aurore@test.com',
            'first_name': 'Aurore',
            'last_name': 'Dupont',
            'password': 'test1234',
        }

        self.client.post(reverse('signup'), data=data)

        user = Customer.objects.get(email='aurore@test.com')

        self.assertNotEqual(user.password, 'test1234')
        self.assertTrue(user.check_password('test1234'))
