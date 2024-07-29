from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ..models.models_ import AccessControl, Applications

MODEL = 'applications'
class AccessControlTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Test Group')
        content_type = ContentType.objects.get_for_model(Applications)
        self.add_permission = Permission.objects.create(
            codename='add_mymodel',
            name='Can add MyModel',
            content_type=content_type
        )
        self.view_permission = Permission.objects.create(
            codename='view_mymodel',
            name='Can view MyModel',
            content_type=content_type
        )
        self.change_permission = Permission.objects.create(
            codename='change_mymodel',
            name='Can change MyModel',
            content_type=content_type
        )
        self.delete_permission = Permission.objects.create(
            codename='delete_mymodel',
            name='Can delete MyModel',
            content_type=content_type
        )

    def test_add_permission_to_group(self):
        """Test add a permission from group"""
        self.group.permissions.add(self.add_permission)
        access_control = AccessControl.objects.get(group=self.group, model=MODEL)
        self.assertTrue(access_control.create)
        self.assertFalse(access_control.read)
        self.assertFalse(access_control.update)
        self.assertFalse(access_control.delete)

    def test_remove_permission_from_group(self):
        """Test remove a permission from group"""
        self.group.permissions.add(self.add_permission)
        self.group.permissions.remove(self.add_permission)
        access_control = AccessControl.objects.get(group=self.group, model=MODEL)
        self.assertFalse(access_control.create)
        self.assertFalse(access_control.read)
        self.assertFalse(access_control.update)
        self.assertFalse(access_control.delete)

    def test_add_multiple_permissions_to_group(self):
        """Test add multiple permissions to a model is successful."""
        self.group.permissions.add(self.add_permission, self.view_permission, self.change_permission)
        access_control = AccessControl.objects.get(group=self.group, model=MODEL)
        self.assertTrue(access_control.create)
        self.assertTrue(access_control.read)
        self.assertTrue(access_control.update)
        self.assertFalse(access_control.delete)

    def test_remove_multiple_permissions_from_group(self):
        """Test remove multiple permissions to a model is successful."""
        self.group.permissions.add(self.add_permission, self.view_permission, self.change_permission)
        self.group.permissions.remove(self.add_permission, self.view_permission)
        access_control = AccessControl.objects.get(group=self.group, model=MODEL)
        self.assertFalse(access_control.create)
        self.assertFalse(access_control.read)
        self.assertTrue(access_control.update)
        self.assertFalse(access_control.delete)

    def test_add_permission_when_access_control_already_exists(self):
        """Test adding a new permission updates the existing record."""
        AccessControl.objects.create(group=self.group, model=MODEL, create=False, read=False, update=False, delete=False)
        self.group.permissions.add(self.add_permission)
        access_control = AccessControl.objects.get(group=self.group, model=MODEL)
        self.assertTrue(access_control.create)
        self.assertFalse(access_control.read)
        self.assertFalse(access_control.update)
        self.assertFalse(access_control.delete)

    def test_remove_permission_when_access_control_already_exists(self):
        """Test removing a new permission updates the existing record."""
        AccessControl.objects.create(group=self.group, model=MODEL, create=True, read=False, update=False, delete=False)
        self.group.permissions.remove(self.add_permission)
        access_control = AccessControl.objects.get(group=self.group, model=MODEL)
        self.assertFalse(access_control.create)
        self.assertFalse(access_control.read)
        self.assertFalse(access_control.update)
        self.assertFalse(access_control.delete)

    def test_no_permissions_in_group(self):
        """Test no permissions is assigned to a group."""
        with self.assertRaises(AccessControl.DoesNotExist):
            AccessControl.objects.get(group=self.group, model=MODEL)

    def tearDown(self):
        self.group.permissions.clear()
        self.group.delete()
        Permission.objects.all().delete()
        AccessControl.objects.all().delete()

