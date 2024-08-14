from django.db import models, transaction
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group
)
from course.models.models import Program
import datetime
from django.conf import settings

class City(models.Model):
    """Cities the Programs are being offerend in."""
    city = models.CharField(max_length=50)
    shortname = models.CharField(max_length=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Batch(models.Model):
    """Batches of cities."""
    batch = models.CharField(max_length=10, primary_key=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    year = models.IntegerField()
    no_of_students = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    # term_choices = [
    #     ('Fall', 'fall'),
    #     ('Winter', 'winter'),
    #     ('Spring', 'spring'),
    #     ('Summer', 'summer'),
    #     ('Annual', 'annual')
    # ]
    # term = models.CharField(max_length=10, choices=term_choices)

    def save(self, *args, **kwargs):
        # Generate the batch code if not provided
        if not self.batch:
            self.batch = f"{self.city.shortname}-{str(self.year)[-2:]}"
        
        # # Assign the term based on the created_at month if term is not provided
        # if not self.term:
        #     if self.created_at and self.created_at.month in [9, 10, 11]:
        #         self.term = 'fall'
        #     elif self.created_at and self.created_at.month in [12, 1, 2]:
        #         self.term = 'winter'
        #     elif self.created_at and self.created_at.month in [3, 4, 5]:
        #         self.term = 'spring'
        #     elif self.created_at and self.created_at.month in [6, 7, 8]:
        #         self.term = 'summer'
        #     else:
        #         self.term = 'annual'  # Default if no match

        super(Batch, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('city', 'year')



class Applications(models.Model):
    """Users of Registration Request"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)  # make first name and last name mandatory
    last_name = models.CharField(max_length=20)
    contact = models.CharField(max_length=12, null=True, blank=True)
    city = models.CharField(max_length=50)
    city_abb = models.CharField(max_length=10)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    year = models.IntegerField(default=datetime.date.today().year)
    application_status_choices = [
        ('approved', 'Approved'),
        ('short_listed', 'Short_Listed'),
        ('pending', 'Pending'),
        ('removed', 'Removed')
    ]
    application_status = models.CharField(max_length= 15, choices= application_status_choices, default='pending') # I added 
    #program_id should also be here
    #area of residence.

#this should have a status field.

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
    is_verified = models.BooleanField(default=False)

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


class Location(models.Model):
    """Available locations in cities."""
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=3)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#location should also tell when the capacity is full

class Sessions(models.Model):
    """Location based sessions."""
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    no_of_students = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

#session should also have a program or program_id.
#session should also have a name.

class Student(models.Model):
    """Extra details of Students in the System."""
    registration_id = models.CharField(max_length=20, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, null=True, blank=True)
    # batch = models.ForeignKey(Batch, on_delete=models.CASCADE)


    # def save(self, *args, **kwargs):
    #     if not self.registration_id:
    #         batch = self.batch.batch
    #         self.registration_id = f"{batch}-{self.user.id}"
    #     super(Student, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('session', 'user')

class Instructor(models.Model):
    """Extra details of Instructors in the System."""
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE
                , related_name='instructor',
                null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)



# class StudentInstructor(models.Model):
#     """Extra details of Students and Instructors in the System."""
#     registration_id = models.CharField(max_length=20, primary_key=True)
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     session = models.ForeignKey(Sessions, on_delete=models.CASCADE, null=True, blank=True)
#     # batch = models.ForeignKey(Batch, on_delete=models.CASCADE)


#     # def save(self, *args, **kwargs):
#     #     if not self.registration_id:
#     #         batch = self.batch.batch
#     #         self.registration_id = f"{batch}-{self.user.id}"
#     #     super(StudentInstructor, self).save(*args, **kwargs)

#     class Meta:
#         unique_together = ('session', 'user')

#need discussion on instructor table, should we go with many to many field here.