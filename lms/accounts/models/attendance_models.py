from django.db import models
from django.conf import settings
import sys

sys.path.append("...")
from .location_models import Sessions
from utils.custom import STATUS_CHOICES
from course.models.models import Course
from .user_models import Student, Instructor, User
from django.utils import timezone


class Attendance(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student"
    )
    date = models.DateField(default=timezone.now)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    status = models.PositiveSmallIntegerField(
            choices=[(0, "Present"), (1, "Absent"), (2, "Leave")],
            default=0,
        )
    marked_by = models.CharField(max_length=50, null=True)

    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student} - {self.date}"

