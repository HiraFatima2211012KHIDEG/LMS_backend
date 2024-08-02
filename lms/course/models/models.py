from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from accounts.models import User
import re

STATUS_CHOICES = (
        (0, 'Not Active'),
        (1, 'Active'),
        (2, 'Deleted'),
    )
class Program(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)

    def __str__(self):
        return self.name


class Course(models.Model):
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="courses", null=True, blank=True
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    credit_hours = models.IntegerField()

    def __str__(self):
        return self.name


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)

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
    # module = models.ForeignKey(Module, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    question = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)
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
        return self.question


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, related_name="submissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_file = models.FileField(
        upload_to="submissions/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "ppt", "pptx", "txt",'zip']
            )
        ],
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    resubmission = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.user} - {self.assignment}"


class Grading(models.Model):
    submission=models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE)
    grade=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_grade=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.submission} - {self.grade}"



class Quizzes(models.Model):
    # module = models.ForeignKey(Module, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    question = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    content = models.FileField(
        upload_to="quizzes/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "ppt", "pptx", "txt",'zip']
            )
        ],
        null=True, blank=True
    )
    due_date = models.DateTimeField()

    def __str__(self):
        return self.question


class QuizSubmission(models.Model):
    quiz = models.ForeignKey(
        Quizzes, related_name="quiz_submissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz_submitted_file = models.FileField(
        upload_to="quiz_submissions/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "ppt", "pptx", "txt",'zip']
            )
        ],
    )
    quiz_submitted_at = models.DateTimeField(auto_now_add=True)
    resubmission = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.user} - {self.quiz}"


class QuizGrading(models.Model):
    quiz_submissions=models.ForeignKey(QuizSubmission, on_delete=models.CASCADE)
    grade=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_grade=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_submissions} - {self.grade}"



class Project(models.Model):
    course = models.ForeignKey(Course, related_name='projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.FileField(
        upload_to="project/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "ppt", "pptx", "txt", "zip"]
            )
        ],
        null=True, blank=True
    )
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class ProjectSubmission(models.Model):
    project = models.ForeignKey(
        Project, related_name="project_submissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_submitted_file = models.FileField(
        upload_to="project_submissions/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "ppt", "pptx", "txt",'zip']
            )
        ],
    )
    project_submitted_at = models.DateTimeField(auto_now_add=True)
    resubmission = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.user} - {self.project}"


class ProjectGrading(models.Model):
    project_submissions=models.ForeignKey(ProjectSubmission, on_delete=models.CASCADE)
    grade=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_grade=models.DecimalField(max_digits=10, decimal_places=2, null=True)
    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_submissions} - {self.grade}"
