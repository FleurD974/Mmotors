from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import Customer
from store.models import Application, Car, Document, DocumentType

class StoreTest(TestCase):
    def setUp(self):
        self.car = Car.objects.create(
            brand= 'Test',
            model='first',
            engine='essence',
            leasing_price=100,
            registration_number='AA-111-AA',
        )
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
        self.application = Application.objects.create(
            customer=self.user,
            car=self.car,
        )

    def test_index_display_home_page(self):
        response= self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Qu'est ce que MMotors")

    def test_connexion_button_shown_when_user_not_connected(self):
        response = self.client.get(reverse('index'))
        self.assertIn('Se connecter', str(response.content))

    def test_redirect_when_anonymous_user_access_application_detail_view(self):
        response = self.client.get(reverse('application-detail'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{reverse('login')}?next={reverse('application-detail')}', status_code=302)

    def test_all_leased_cars_only_returns_available_leased_cars(self):
        leased_available = Car.objects.create(
            brand= 'Car',
            model='first',
            engine='essence',
            leasing_price=100,
            registration_number='AA-111-AA',
            is_leased=True,
            is_available=True,
        )

        Car.objects.create(
            brand= 'Car',
            model='second',
            engine='essence',
            leasing_price=100,
            registration_number='AA-222-AA',
            is_leased=False,
            is_available=True,
        )

        Car.objects.create(
            brand= 'Car',
            model='third',
            engine='essence',
            leasing_price=100,
            registration_number='AA-333-AA',
            is_leased=True,
            is_available=False,
        )

        response = self.client.get(reverse('all-leased-cars'))
        cars = response.context['cars']

        self.assertEqual(list(cars), [self.car, leased_available])

    def test_all_purchased_cars_only_returns_available_leased_cars(self):
        purchased_available = Car.objects.create(
            brand= 'Car',
            model='first',
            engine='essence',
            leasing_price=100,
            registration_number='AA-111-AA',
            is_purchased=True,
            is_leased=False,
            is_available=True,
        )

        Car.objects.create(
            brand= 'Car',
            model='second',
            engine='essence',
            leasing_price=100,
            registration_number='AA-222-AA',
            is_purchased=False,
            is_available=True,
        )

        Car.objects.create(
            brand= 'Car',
            model='third',
            engine='essence',
            leasing_price=100,
            registration_number='AA-333-AA',
            is_purchased=True,
            is_leased=False,
            is_available=False,
        )

        response = self.client.get(reverse('all-purchased-cars'))
        cars = response.context['cars']

        self.assertEqual(list(cars), [purchased_available])

    def test_upload_document_requires_login(self):
        response = self.client.get(
            reverse('upload-document', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 302)

    def test_upload_document_forbidden_if_not_owner(self):
        other_user = Customer.objects.create_user(
            email='other@test.com',
            first_name='Other',
            last_name='Test',
            password='test1234'
        )
        self.client.login(email='other@test.com', password='test1234')

        response = self.client.get(
            reverse('upload-document', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 403)
        
    def test_upload_document_forbidden_if_application_not_draft(self):
        self.application.status = 'submitted'
        self.application.save()
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(
            reverse('upload-document', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_upload_document_get(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(
            reverse('upload-document', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/upload.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['application'], self.application)

    def test_upload_document_success(self):
        self.client.login(email='fleur@test.com', password='test123')
        document_type = DocumentType.objects.create(name="Identity")
        file = SimpleUploadedFile(
            'test.pdf',
            b"fake pdf content",
            content_type='application/pdf'
        )

        response = self.client.post(
            reverse('upload-document', kwargs={'application_id': self.application.id}),
            data={
                'type': document_type.pk,
                'file': file,
            },
            follow=True,
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertIn(
            "Document ajouté avec succès",
            [str(m) for m in messages]
        )
        self.assertEqual(self.application.documents.count(), 1)

    def test_upload_document_do_not_add_if_duplicate_type(self):
        existing = SimpleUploadedFile(
            'existing.pdf',
            b'content',
            content_type='application/pdf'
        )
        document_type = DocumentType.objects.create(name="Identity")


        Document.objects.create(
            application=self.application,
            type=document_type,
            file=existing
        )
        self.client.login(email='fleur@test.com', password='test123')

        new_file = SimpleUploadedFile(
            'new.pdf',
            b'content',
            content_type='application/pdf'
        )

        response = self.client.post(
            reverse('upload-document', kwargs={'application_id': self.application.id}),
            {
                'type': document_type.pk,
                'file': new_file,
            },
            follow=True
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertIn(
            "Un document de ce type a déjà été ajouté",
            [str(m) for m in messages]
        )
        self.assertEqual(self.application.documents.count(), 1)
        self.assertEqual(self.application.documents.count(), 1)

    def test_application_detail(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(reverse('application-detail'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/application.html')
        self.assertEqual(response.context['application'], self.application)

    def test_application_detail_requires_login(self):
        response = self.client.get(reverse('application-detail'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("application-detail")}'
        )
        
    def test_application_not_found(self):
        Customer.objects.create_user(
            email='charlie@test.com',
            first_name='charlie',
            last_name='Test',
            password='test456',
        )
        self.client.login(email='charlie@test.com', password='test456')

        response = self.client.get(reverse('application-detail'))

        self.assertEqual(response.status_code, 404)
        
    def test_staff_can_access_all_cars(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(reverse('all-cars'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/allcars.html')

    def test_non_staff_cannot_access_all_cars(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(reverse('all-cars'))

        self.assertEqual(response.status_code, 403)

class SubmitApplicationViewTest(TestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            email='fleur@test.com',
            first_name='fleur',
            last_name='Test',
            password='test123',
        )
        self.second_user = Customer.objects.create_user(
            email='john@test.com',
            first_name='John',
            last_name='Doe',
            password='test456',
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

    def test_submit_application_success(self):
        self.client.login(email='fleur@test.com', password='test123')
        response = self.client.get(
            reverse('submit-application', kwargs={'application_id': self.application.id})
        )

        self.application.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.application.status, 'submitted')
        self.assertRedirects(response, reverse("application-detail"))

    def test_submit_application_success_message(self):
        self.client.login(email='fleur@test.com', password='test123')
        response = self.client.get(
            reverse('submit-application', kwargs={'application_id': self.application.id}),
            follow=True
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Application soumise avec succès')

    def test_submit_application_forbidden(self):
        self.client.login(email='john@test.com', password='test456')
        response = self.client.get(
            reverse('submit-application', kwargs={'application_id': self.application.id})
        )

        self.application.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.application.status, 'draft')

    def test_submit_application_requires_login(self):
        response = self.client.get(
            reverse('submit-application', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

class ApplicationTreatmentTest(TestCase):
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

    def test_staff_can_access_all_applications(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(reverse('all-applications'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/applications.html')

    def test_non_staff_cannot_access_all_applications(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(reverse('all-applications'))

        self.assertEqual(response.status_code, 302)

    def test_all_applications_display_only_submitted_application(self):
        second_user = Customer.objects.create_user(
            email='usef@test.com',
            first_name='user',
            last_name='Test',
            password='test456',
        )
        Application.objects.create(
            customer=second_user,
            car=self.car,
            status='submitted'
        )

        self.client.login(email='admin@test.com', password='test456')
        response = self.client.get(reverse('all-applications'))
        applications = response.context['applications']

        self.assertEqual(applications.count(), 1)
        self.assertEqual(applications.first().status, 'submitted')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('admin-application-detail', kwargs={'application_id': self.application.id})
        )

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse(
                "admin-application-detail",
                kwargs={'application_id': self.application.id}
            )}'
        )

    def test_forbidden_if_not_staff(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(
            reverse('admin-application-detail', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_view_application_detail(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(
            reverse('admin-application-detail', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/review.html')

        self.assertEqual(response.context['application'], self.application)
        self.assertEqual(
            list(response.context['documents']),
            list(self.application.documents.all())
        )

    def test_application_not_found_returns_404(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(
            reverse('admin-application-detail', kwargs={'application_id': 99999})
        )

        self.assertEqual(response.status_code, 404)

    def test_approve_application_redirects_if_not_logged_in(self):
        response = self.client.get(
            reverse('approve-application', kwargs={'application_id': self.application.id})
        )

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse(
                'approve-application',
                kwargs={'application_id': self.application.id}
            )}'
        )

    def test_approve_application_forbids_if_not_staff(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(
            reverse('approve-application', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_approve_if_not_submitted(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(
            reverse('approve-application', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_approve_if_application_not_found(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(
            reverse('approve-application', kwargs={'application_id': 99999})
        )

        self.assertEqual(response.status_code, 404)

    def test_approve_application_success(self):
        self.client.login(email='admin@test.com', password='test456')

        self.application.status = 'submitted'
        self.application.save()

        response = self.client.get(
            reverse('approve-application', kwargs={'application_id': self.application.id})
        )

        self.application.refresh_from_db()

        self.assertEqual(self.application.status, 'approved')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/applications.html')

    def test_reject_application_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('reject-application', kwargs={'application_id': self.application.id})
        )

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse(
                "reject-application",
                kwargs={'application_id': self.application.id}
            )}'
        )

    def test_reject_application_forbids_if_not_staff(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(
            reverse('reject-application', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_reject_if_not_submitted(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(
            reverse('reject-application', kwargs={'application_id': self.application.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_reject_if_application_not_found(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(
            reverse('reject-application', kwargs={'application_id': 99999})
        )

        self.assertEqual(response.status_code, 404)

    def test_reject_application_success(self):
        self.client.login(email='admin@test.com', password='test456')

        self.application.status = 'submitted'
        self.application.save()

        response = self.client.get(
            reverse('reject-application', kwargs={'application_id': self.application.id})
        )

        self.application.refresh_from_db()

        self.assertEqual(self.application.status, 'rejected')
        self.assertEqual(response.status_code, 200)

class ModifyViewTest(TestCase):
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
            brand= 'Renault',
            model='Clio',
            engine='Essence',
            leasing_price=100,
            registration_number='AA-111-AA',
        )

        self.url = reverse('modify-car', kwargs={'car_id': self.car.id})

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={self.url}'
        )

    def test_forbidden_if_not_staff(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_modify_car_form(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/modifycar.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['car'], self.car)

    def test_post_valid_form_updates_car(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.post(self.url, data={
            'brand': 'Renault',
            'model': 'Clio 2',
            'engine': 'Essence',
            'mileage': 12000,
            'passenger_number': 5,
            'is_purchased': True,
            'is_leased': False,
            'purchase_price': 11000,
            'leasing_price': 200,
            'registration_number': 'AA-123-AA',
            'description': 'updated'
        })

        self.car.refresh_from_db()

        self.assertEqual(self.car.model, 'Clio 2')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)

    def test_post_invalid_both_true(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.post(self.url, data={
            'brand': 'Renault',
            'model': 'Clio',
            'engine': 'Essence',
            'mileage': 10000,
            'passenger_number': 5,
            'is_purchased': True,
            'is_leased': True,
            'purchase_price': 10000,
            'leasing_price': 200,
            'registration_number': 'AA-123-AA',
            'description': 'desc'
        })

        self.assertEqual(response.status_code, 200)

        form = response.context['form']

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Une voiture ne peut pas être en location et à l\'achat.',
            form.non_field_errors()
        )

    def test_post_invalid_both_false(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.post(self.url, data={
            'brand': 'Renault',
            'model': 'Clio',
            'engine': 'Essence',
            'mileage': 10000,
            'passenger_number': 5,
            'is_purchased': False,
            'is_leased': False,
            'purchase_price': 10000,
            'leasing_price': 200,
            'registration_number': 'AA-123-AA',
            'description': 'desc'
        })

        self.assertEqual(response.status_code, 200)

        form = response.context['form']

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Une voiture doit être en location ou à l\'achat.',
            form.non_field_errors()
        )

class AddCarViewTest(TestCase):
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
        self.url = reverse('add-car')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={self.url}'
        )

    def test_forbidden_if_not_staff(self):
        self.client.login(email='fleur@test.com', password='test123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_add_car_form(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/addcar.html')
        self.assertIn('form', response.context)

    def test_post_valid_creates_car(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.post(self.url, data={
            'brand': 'Peugeot',
            'model': '208',
            'engine': 'Diesel',
            'mileage': 5000,
            'passenger_number': 5,
            'is_purchased': True,
            'is_leased': False,
            'purchase_price': 15000,
            'leasing_price': 300,
            'registration_number': 'BB-456-BB',
            'description': 'New car'
        })

        self.assertEqual(Car.objects.count(), 1)

        car = Car.objects.first()
        self.assertEqual(car.model, '208')

        self.assertRedirects(response, reverse('all-cars'))

    def test_post_invalid_both_true(self):
        self.client.login(email='admin@test.com', password='test456')

        response = self.client.post(self.url, data={
            'brand': 'Peugeot',
            'model': '208',
            'engine': 'Diesel',
            'mileage': 5000,
            'passenger_number': 5,
            'is_purchased': True,
            'is_leased': True,
            'purchase_price': 15000,
            'leasing_price': 300,
            'registration_number': 'BB-456-BB',
            'description': 'New car'
        })

        self.assertEqual(Car.objects.count(), 0)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Une voiture ne peut pas être en location et à l\'achat.',
            form.non_field_errors()
        )
