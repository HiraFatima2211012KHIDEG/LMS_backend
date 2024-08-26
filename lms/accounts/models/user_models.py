from django.db import models, transaction
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
)
from course.models.program_model import Program
import datetime
from django.conf import settings
from .location_models import (
    Sessions,
)
from utils.custom import STATUS_CHOICES
from course.models.models import Course


class Applications(models.Model):
    """Users of Registration Request"""

    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=20
    )  # make first name and last name mandatory
    last_name = models.CharField(max_length=20)
    contact = models.CharField(max_length=12, null=True, blank=True)
    city = models.CharField(max_length=50)
    city_abb = models.CharField(max_length=10, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    group_name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    year = models.IntegerField(default=datetime.date.today().year)
    application_status_choices = [
        ("approved", "Approved"),
        ("short_listed", "Short_Listed"),
        ("pending", "Pending"),
        ("removed", "Removed"),
    ]
    application_status = models.CharField(
        max_length=15, choices=application_status_choices, default="pending"
    )  # I added
    # program_id should also be here
    # area of residence.


# this should have a status field.

#this should have a status field.
    def __str__(self):
        return f"{self.email} - {self.city} - {self.program}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

    def create_admin(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_verified", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Admin user must have is_staff=True.")

        user = self.create_user(email, password, **extra_fields)

        admin_group, created = Group.objects.get_or_create(name="admin")
        user.groups.add(admin_group)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    contact = models.CharField(max_length=12, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.id:
            with transaction.atomic():
                group_id_ranges = {
                    "admin": (2, 99),
                    "HOD": (100, 999),
                    "instructor": (1000, 9999),
                    "student": (10000, 99999),
                }

                if self.is_superuser:
                    self.id = 1
                elif self.is_staff:
                    last_admin = User.objects.filter(id__gte=2, id__lte=99).last()
                    self.id = last_admin.id + 1 if last_admin else 2
                else:
                    try:
                        application = Applications.objects.get(email=self.email)
                        user_group_name = application.group_name
                    except Applications.DoesNotExist:
                        raise ValueError("User must be associated with an application.")

                    if user_group_name not in group_id_ranges:
                        raise ValueError(
                            "User group must be one of: admin, HOD, instructor, student"
                        )

                    start, end = group_id_ranges[user_group_name]
                    last_user = User.objects.filter(id__gte=start, id__lte=end).last()
                    self.id = last_user.id + 1 if last_user else start

                    try:
                        group = Group.objects.get(name=user_group_name)
                        super(User, self).save(*args, **kwargs)
                        self.groups.add(group)
                    except Group.DoesNotExist:
                        raise ValueError(f"Group '{user_group_name}' does not exist.")

        super(User, self).save(*args, **kwargs)


class AccessControl(models.Model):
    """access privileges of user groups in the system."""

    model = models.CharField(max_length=50)
    create = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    update = models.BooleanField(default=False)
    remove = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Student(models.Model):
    """Extra details of Students in the System."""

    registration_id = models.CharField(max_length=20, primary_key=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session = models.ForeignKey(
        Sessions, on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.registration_id:
            batch = self.batch.batch
            self.registration_id = f"{batch}-{self.user.id}"
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.registration_id}"
    # class Meta:
    #     unique_together = ('batch', 'user')

    class Meta:
        unique_together = ("session", "user")


class Instructor(models.Model):
    """Extra details of Instructors in the System."""

    id = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        to_field="email",
        related_name="instructor_profile",
    )
    session = models.ManyToManyField(Sessions)
    courses = models.ManyToManyField(Course)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.id.email
