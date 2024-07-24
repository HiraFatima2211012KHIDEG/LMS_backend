from typing import Any
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager for users in the system"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new user"""
        if not email:
            raise ValueError("user must have an email address")
        user = self.model(email = self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """Create and save new superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        return user

    def create_admin(self, email, password=None):
        """Create and save new admin"""
        user = self.create_user(email, password)
        user.is_admin = True
        user.is_staff = True
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    contact = models.CharField(max_length=12, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.username


class Applications(models.Model):
    """Users of Registration Request"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    contact = models.CharField(max_length=12, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
