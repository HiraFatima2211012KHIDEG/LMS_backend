from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
# from django.core.exceptions import ValidationError
# from accounts.models.user_models import Instructor
from django.utils import timezone
from accounts.models.location_models import Sessions
import re

STATUS_CHOICES = (
        (0, 'Not Active'),
        (1, 'Active'),
        (2, 'Deleted'),
    )


class Skill(models.Model):
    skill_name=models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.skill_name

class Course(models.Model):
    name = models.CharField(max_length=100)
    short_description = models.TextField()
    about = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    theory_credit_hours = models.IntegerField(blank=True, default=0)
    lab_credit_hours = models.IntegerField(blank=True, default=0)
    skills = models.ManyToManyField('Skill',  blank=True)
    instructors = models.ManyToManyField('accounts.Instructor', blank=True)
    picture=models.TextField(null=True, blank=True)
    # start_date = models.DateField()
    # end_date = models.DateField()
    def __str__(self):
        return self.name


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    name = models.CharField(max_length=100)
    description = models.TextField()
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return self.name

class ContentFile(models.Model):
    module = models.ForeignKey(
        Module, related_name="files", on_delete=models.CASCADE, null=True, blank=True
    )
    file = models.TextField()
    def __str__(self):
        return f"{self.module} - {self.file}"

class Assignment(models.Model):
    # module = models.ForeignKey(Module, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_grade = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    question = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)
    content = models.TextField()
    no_of_resubmissions_allowed = models.IntegerField(default=0)
    due_date = models.DateTimeField()
    late_submission = models.BooleanField(default=False)

    def get_due_date_in_user_timezone(self, user_timezone):
        # Convert due_date to the user's time zone
        return timezone.localtime(self.due_date, timezone.pytz.timezone(user_timezone))
    def __str__(self):
        return self.question


ASSESMENT_STATUS_CHOICES = (
        (0, 'Not Submitted'),
        (1, 'Submitted'),
        (2, 'Pending'),
    )

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, related_name="submissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registration_id = models.CharField(max_length=50, null=True, blank=True)
    submitted_file = models.TextField()
    status = models.PositiveSmallIntegerField(choices=ASSESMENT_STATUS_CHOICES, default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remaining_resubmissions = models.IntegerField(default=0)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.assignment}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.remaining_resubmissions = self.assignment.no_of_resubmissions_allowed
            print(f"Initialized remaining_resubmissions with {self.remaining_resubmissions}")

        super().save(*args, **kwargs)

    def decrement_resubmissions(self):
        if self.remaining_resubmissions > 0:
            self.remaining_resubmissions -= 1

            self.save()
            return True
        return False

# class Grading(models.Model):
#     submission=models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE)
#     grade=models.DecimalField(max_digits=10, decimal_places=2, null=True)
#     total_grade=models.DecimalField(max_digits=10, decimal_places=2, null=True)
#     feedback = models.TextField(null=True, blank=True)
#     graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     graded_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.submission} - {self.grade}"

class Grading(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    # total_grade = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.submission} - {self.grade}"


class Quizzes(models.Model):
    # module = models.ForeignKey(Module, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_grade = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    question = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    content = models.TextField()
    no_of_resubmissions_allowed = models.IntegerField(default=0)
    due_date = models.DateTimeField()
    late_submission = models.BooleanField(default=False)

    def __str__(self):
        return self.question


class QuizSubmission(models.Model):
    quiz = models.ForeignKey(
        Quizzes, related_name="quiz_submissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registration_id = models.CharField(max_length=50, null=True, blank=True)
    submitted_file = models.TextField()
    status = models.PositiveSmallIntegerField(choices=ASSESMENT_STATUS_CHOICES, default=0)
    quiz_submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remaining_resubmissions = models.IntegerField(default=0)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.quiz}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.remaining_resubmissions = self.quiz.no_of_resubmissions_allowed
            print(f"Initialized remaining_resubmissions with {self.remaining_resubmissions}")

        super().save(*args, **kwargs)

    def decrement_resubmissions(self):
        if self.remaining_resubmissions > 0:
            self.remaining_resubmissions -= 1
            self.save()
            return True
        return False


class QuizGrading(models.Model):
    quiz_submissions=models.ForeignKey(QuizSubmission, on_delete=models.CASCADE)
    grade=models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quiz_submissions} - {self.grade}"



class Project(models.Model):
    course = models.ForeignKey(Course, related_name='projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    due_date = models.DateTimeField()
    total_grade = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    no_of_resubmissions_allowed = models.IntegerField(default=0)
    late_submission = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ProjectSubmission(models.Model):
    project = models.ForeignKey(
        Project, related_name="project_submissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registration_id = models.CharField(max_length=50, null=True, blank=True)
    submitted_file = models.TextField()
    status = models.PositiveSmallIntegerField(choices=ASSESMENT_STATUS_CHOICES, default=0)
    project_submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remaining_resubmissions = models.IntegerField(default=0)
    comments = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.user} - {self.project}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.remaining_resubmissions = self.project.no_of_resubmissions_allowed
            print(f"Initialized remaining_resubmissions with {self.remaining_resubmissions}")

        super().save(*args, **kwargs)

    def decrement_resubmissions(self):
        if self.remaining_resubmissions > 0:
            self.remaining_resubmissions -= 1
            self.save()
            return True
        return False

class ProjectGrading(models.Model):
    project_submissions=models.ForeignKey(ProjectSubmission, on_delete=models.CASCADE)
    grade=models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)

    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_submissions} - {self.grade}"


class Exam(models.Model):
    course = models.ForeignKey(Course, related_name='exams', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    due_date = models.DateField()
    total_grade = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    late_submission = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class ExamSubmission(models.Model):
    exam = models.ForeignKey(
        Exam, related_name="exam_submissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registration_id = models.CharField(max_length=50, null=True, blank=True)
    submitted_file = models.TextField()
    status = models.PositiveSmallIntegerField(choices=ASSESMENT_STATUS_CHOICES, default=0)
    exam_submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resubmission = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.exam}"

class ExamGrading(models.Model):
    exam_submission = models.ForeignKey(ExamSubmission, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    feedback = models.TextField(null=True, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.exam_submission} - {self.grade}"


class Weightage(models.Model):
    course = models.ForeignKey(Course, related_name='weightage', on_delete=models.CASCADE)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE,null=True, blank=True)
    assignments_weightage = models.FloatField(default=0,null=True, blank=True)
    quizzes_weightage = models.FloatField(default=0,null=True, blank=True)
    projects_weightage = models.FloatField(default=0,null=True, blank=True)
    exams_weightage = models.FloatField(default=0,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)
