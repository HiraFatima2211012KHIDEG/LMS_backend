"""
Tests for Models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth.models import Group
from ..models.models_ import AccessControl
import constants
from ..views import get_group_permissions


def create_user(email='user@example.com', password='testpass'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """ Test models. """

    def test_create_application_with_email_successful(self):
        """ Test creating user with an email is successful. """
        email = 'test@example.com'
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_email_normalized(self):
        """ Test email is normalized for new user. """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

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


class GetGroupPermissionsTestCase(TestCase):

    def setUp(self):
        self.group = Group.objects.create(name='Test Group')

        self.access_control1 = AccessControl.objects.create(
            group=self.group,
            model='applications',
            create=True,
            read=False,
            update=True,
            delete=False
        )

        self.access_control2 = AccessControl.objects.create(
            group=self.group,
            model='other_model',
            create=False,
            read=True,
            update=False,
            delete=True
        )

    def test_get_group_permissions(self):
        """test retrieving the permissions related to group id."""
        permissions = get_group_permissions(self.group.id)

        self.assertEqual(permissions['applications'], f"{constants.CREATE}{constants.UPDATE}")
        self.assertEqual(permissions['other_model'], f"{constants.READ}{constants.DELETE}")

    def test_get_group_permissions_no_access_controls(self):
        """Test no permissions for newly created group without permissions."""
        new_group = Group.objects.create(name='New Group')
        permissions = get_group_permissions(new_group.id)
        self.assertEqual(permissions, {})

    def test_get_group_permissions_no_permissions_set(self):
        """Test no access permissions are assigned to a group."""
        AccessControl.objects.create(
            group=self.group,
            model='empty_model',
            create=False,
            read=False,
            update=False,
            delete=False
        )

        permissions = get_group_permissions(self.group.id)
        self.assertEqual(permissions['empty_model'], '')

    def test_get_group_permissions_multiple_entries_same_model(self):
        """Test getting all the permission related to model."""
        AccessControl.objects.create(
            group=self.group,
            model='applications',
            create=False,
            read=True,
            update=False,
            delete=True
        )

        permissions = get_group_permissions(self.group.id)
        expected_permissions = f"{constants.READ}{constants.DELETE}"
        self.assertEqual(permissions['applications'], expected_permissions)


    def tearDown(self):
        self.group.delete()
        AccessControl.objects.all().delete()
