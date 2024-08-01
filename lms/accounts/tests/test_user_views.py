"""
Tests for Models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from ..models.models_ import User
from ..models.models_ import Applications


def create_user(email='user@example.com', password='testpass'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """ Test models. """

    def test_create_application_with_email_successful(self):
        """ Test creating user with an email is successful. """
        email = 'test@example.com'
        password = 'testpassword'
        user = Applications.objects.create(
            email=email
        )
        self.assertEqual(user.email, email)

    def test_new_application_without_email_raises_error(self):
        """ Test that creating a user without email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """ Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class CreateUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.create_url = reverse('create')
        self.admin_group = Group.objects.create(name='admin')
        self.hod_group = Group.objects.create(name='HOD')
        self.instructor_group = Group.objects.create(name='instructor')
        self.student_group = Group.objects.create(name='student')


    def create_application(self, email, group_name):
        return Applications.objects.create(email=email, group_name=group_name)

    def test_create_admin_user(self):
        email = 'admin@example.com'
        self.create_application(email, 'admin')
        response = self.client.post(self.create_url, {
            'email': email,
            'password': 'Password&123',
            'first_name': 'Admin',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(email=email).id, 2)

    def test_create_hod_user(self):
        email = 'hod@example.com'
        self.create_application(email, 'HOD')
        response = self.client.post(self.create_url, {
            'email': email,
            'password': 'Password&123',
            'first_name': 'HOD',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(email=email).id, 100)

    def test_create_instructor_user(self):
        email = 'instructor@example.com'
        self.create_application(email, 'instructor')
        response = self.client.post(self.create_url, {
            'email': email,
            'password': 'Password&123',
            'first_name': 'Instructor',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(email=email).id, 1000)

    def test_create_student_user(self):
        email = 'student@example.com'
        self.create_application(email, 'student')
        response = self.client.post(self.create_url, {
            'email': email,
            'password': 'Password&123',
            'first_name': 'Student',
            'last_name': 'User'
        })
        self.assertEqual(User.objects.get(email=email).id, 10000)

    def test_create_superuser(self):
        email = 'superuser@example.com'
        response = get_user_model().objects.create_superuser(
            email=email,
            password='Password&123',
        )
        self.assertEqual(User.objects.get(email=email).id, 1)

    def test_create_user_no_application(self):
        email = 'noapp@example.com'
        with self.assertRaises(ValueError):
            self.client.post(self.create_url, {
                'email': email,
                'password': 'Password&123',
                'first_name': 'No',
                'last_name': 'Application'
            })

    def test_create_user_invalid_group(self):
        email = 'invalidgroup@example.com'
        self.create_application(email, 'invalidgroup')
        with self.assertRaises(ValueError):
            self.client.post(self.create_url, {
                'email': email,
                'password': 'Password&123',
                'first_name': 'Invalid',
                'last_name': 'Group'
            })


