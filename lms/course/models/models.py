from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from accounts.models import User
import re


class Program(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="courses", null=True, blank=True
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    credit_hours = models.IntegerField()

    def __str__(self):
        return self.name


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# def validate_video_url(value):
#     """Validator to ensure the URL is a valid video URL."""
#     if value and not re.match(r'^.*\.(mp4|avi|mov|mkv)$', value):
#         raise ValidationError('Invalid video URL. Only .mp4, .avi, .mov, and .mkv files are allowed.')


class Content(models.Model):
    module = models.ForeignKey(
        Module, related_name="contents", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ContentFile(models.Model):
    content = models.ForeignKey(Content, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="content/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "docx", "ppt", "xls", "zip"]
            )
        ],
    )


class Assignment(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    question = models.TextField()
    description = models.TextField()
    content = models.FileField(
        upload_to="assignments/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "ppt", "pptx", "txt",'zip']
            )
        ],
        null=True, blank=True
    )
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, related_name="submissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name="user_submissions", on_delete=models.CASCADE
    )
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_file = models.FileField(
        upload_to="submissions/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "ppt", "pptx", "txt",'zip']
            )
        ],
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.assignment}"
