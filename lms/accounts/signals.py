"""
signals for accounts app.
"""

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from .models import AccessControl
from accounts.utils import send_email
from django.core.signing import TimestampSigner
import base64
from django.core.signing import TimestampSigner
from django.dispatch import receiver
from .models import User
from django.db import transaction
from django.contrib.auth.models import Group
import os


FRONTEND_URL = os.getenv("FRONTEND_URL")


@receiver(m2m_changed, sender=Group.permissions.through)
def update_access_control(sender, instance, action, reverse, pk_set, **kwargs):
    """update the access control when where new permission is added or removed from a group."""
    if action in {"post_add", "post_remove"}:
        for permission_id in pk_set:
            try:
                permission = Permission.objects.get(id=permission_id)
                content_type = permission.content_type
                model_name = content_type.model
                group = instance if not reverse else Group.objects.get(id=instance.pk)

                access_control, created = AccessControl.objects.get_or_create(
                    model=model_name, group=group
                )
                perm_map = {
                    "add": "create",
                    "view": "read",
                    "change": "update",
                    "delete": "remove",
                }
                for perm_prefix, access_field in perm_map.items():
                    if permission.codename.startswith(f"{perm_prefix}_"):
                        setattr(access_control, access_field, (action == "post_add"))
                        break
                access_control.save()

                if not (
                    access_control.create
                    or access_control.read
                    or access_control.update
                    or access_control.remove
                ):
                    access_control.delete()

            except Permission.DoesNotExist:
                print(f"Permission with id {permission_id} does not exist.")


m2m_changed.connect(update_access_control, sender=Group.permissions.through)


@receiver(m2m_changed, sender=User.groups.through)
def send_verification_email(sender, instance, action, **kwargs):
    # Check if the action is 'post_add' which means the group has been added
    if action == "post_add":
        if instance.groups.filter(name="admin").exists():
            print(f"Signal triggered for admin user: {instance.email}")
            token = create_signed_token(instance.id, instance.email)
            print("Generated token:", token)
            verification_link = f"{FRONTEND_URL}/auth/account-verify/{token}"
            body = (
                f"Congratulations {instance.first_name} {instance.last_name}!\n"
                f"Please click the following link to verify your account:\n{verification_link}"
            )
            email_data = {
                "email_subject": "Verify your account",
                "body": body,
                "to_email": instance.email,
            }
            send_email(email_data)
            print("Verification email sent to:", instance.email)


def create_signed_token(user_id, email):
    signer = TimestampSigner()
    # Combine the user_id and email into a single string
    data = f"{user_id}:{email}"
    # Encode the data with base64
    encoded_data = base64.urlsafe_b64encode(data.encode()).decode()
    # Sign the encoded data
    signed_token = signer.sign(encoded_data)
    return signed_token


m2m_changed.connect(send_verification_email, sender=User.groups.through)
