"""
signals for accounts app.
"""
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from .models import AccessControl

@receiver(m2m_changed, sender=Group.permissions.through)
def update_access_control(sender, instance, action, reverse, pk_set, **kwargs):
    """update the access control when where new permission is added or removed from a group."""
    if action in {'post_add', 'post_remove'}:
        for permission_id in pk_set:
            try:
                permission = Permission.objects.get(id=permission_id)
                content_type = permission.content_type
                model_name = content_type.model
                group = instance if not reverse else Group.objects.get(id=instance.pk)

                access_control, created = AccessControl.objects.get_or_create(
                    model=model_name,
                    group=group
                )
                perm_map = {
                    'add': 'create',
                    'view': 'read',
                    'change': 'update',
                    'delete': 'remove'
                }
                for perm_prefix, access_field in perm_map.items():
                    if permission.codename.startswith(f'{perm_prefix}_'):
                        setattr(access_control, access_field, (action == 'post_add'))
                        break
                access_control.save()

                if not (access_control.create or access_control.read or access_control.update or access_control.remove):
                    access_control.delete()

            except Permission.DoesNotExist:
                print(f"Permission with id {permission_id} does not exist.")

m2m_changed.connect(update_access_control, sender=Group.permissions.through)
