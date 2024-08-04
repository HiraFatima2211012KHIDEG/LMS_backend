from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from ..models.models_ import Applications

class CreateApplicationViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('create-application')  

        self.valid_payload = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'contact': '1234567890',
            'city': 'New York',
            'group_name': 'student'
        }

        self.invalid_payload_email = {
            'email': 'not-an-email',
            'first_name': 'John',
            'last_name': 'Doe',
            'contact': '1234567890',
            'city': 'New York',
            'group_name': 'student'
        }

        self.missing_email_payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'contact': '1234567890',
            'city': 'New York',
            'group_name': 'student'
        }

        self.duplicate_email_payload = {
            'email': 'test@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'contact': '0987654321',
            'city': 'Los Angeles',
            'group_name': 'HOD'
        }

    def test_create_valid_application(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Applications.objects.count(), 1)
        self.assertEqual(Applications.objects.get().email, 'test@example.com')

    def test_create_application_with_invalid_email(self):
        response = self.client.post(self.url, self.invalid_payload_email, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_application_with_missing_email(self):
        response = self.client.post(self.url, self.missing_email_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_application_with_duplicate_email(self):
        self.client.post(self.url, self.valid_payload, format='json')  # Create the first application
        response = self.client.post(self.url, self.duplicate_email_payload, format='json')  # Attempt to create a duplicate
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Applications.objects.count(), 1)

    def test_create_application_with_optional_fields_missing(self):
        payload = {
            'email': 'optional@example.com',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Applications.objects.count(), 1)
        application = Applications.objects.get()
        self.assertEqual(application.email, 'optional@example.com')
        self.assertIsNone(application.first_name)
        self.assertIsNone(application.last_name)
        self.assertIsNone(application.contact)
        self.assertIsNone(application.city)
        self.assertIsNone(application.group_name)

    def test_create_application_with_all_optional_fields(self):
        payload = {
            'email': 'optional@example.com',
            'first_name': '',
            'last_name': '',
            'contact': '',
            'city': '',
            'group_name': ''
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Applications.objects.count(), 1)
        application = Applications.objects.get()
        self.assertEqual(application.email, 'optional@example.com')
        self.assertEqual(application.first_name, '')
        self.assertEqual(application.last_name, '')
        self.assertEqual(application.contact, '')
        self.assertEqual(application.city, '')
        self.assertEqual(application.group_name, '')

