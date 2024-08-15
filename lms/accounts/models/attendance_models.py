from django.db import models
from django.conf import settings
import sys

sys.path.append("...")
from .location_models import Sessions
from course.models.models import Course
from .user_models import Student, Instructor


class Attendance(models.Model):
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student"
    )
    date = models.DateField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    status = models.CharField(
        max_length=10,
        choices=[("Present", "Present"), ("Absent", "Absent"), ("Leave", "Leave")],
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return f"{self.student} - {self.session} - {self.date}"
