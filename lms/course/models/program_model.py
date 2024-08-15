from django.db import models
from .models import *
from accounts.models.location_models import *
from .models import STATUS_CHOICES


class Program(models.Model):
    name = models.CharField(max_length=255, unique=True)
    short_description = models.TextField()
    about = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registration_id = models.CharField(max_length=50, null=True, blank=True)
    courses = models.ManyToManyField(Course)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    picture = models.ImageField(upload_to='material/program_pictures/', blank=True, null=True)

    def __str__(self):
        return self.name

 