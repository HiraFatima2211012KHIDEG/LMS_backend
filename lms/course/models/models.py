from django.db import models
from django.conf import settings

class Program(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=100)

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Course(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    credit_hours = models.IntegerField()

    def __str__(self):
        return self.name

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

