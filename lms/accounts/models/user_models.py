from django.db import models, transaction
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group
)
from .location_models import (
    Sessions,
    Batch
)


class Applications(models.Model):
    """Users of Registration Request"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    contact = models.CharField(max_length=12, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    group_name = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)


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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    contact = models.CharField(max_length=12, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.id:
            with transaction.atomic():
                group_id_ranges = {
                    'admin': (2, 99),
                    'HOD': (100, 999),
                    'instructor': (1000, 9999),
                    'student': (10000, 99999)
                }

                if self.is_superuser:
                    self.id = 1
                else:
                    try:
                        application = Applications.objects.get(email=self.email)
                        user_group_name = application.group_name
                    except Applications.DoesNotExist:
                        raise ValueError("User must be associated with an application.")

                    if user_group_name not in group_id_ranges:
                        raise ValueError("User group must be one of: admin, HOD, instructor, student")

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
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)


class StudentInstructor(models.Model):
    """Extra details of Students and Instructors in the System."""
    registration_id = models.CharField(max_length=20, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if not self.registration_id:
            batch = self.batch.batch
            self.registration_id = f"{batch}-{self.user.id}"
        super(StudentInstructor, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('batch', 'user')
