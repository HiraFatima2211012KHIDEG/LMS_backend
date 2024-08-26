from django.db import models
from django.conf import settings
import sys

sys.path.append("...")
from .location_models import Sessions
from utils.custom import STATUS_CHOICES
from course.models.models import Course
from .user_models import Student, Instructor


class Attendance(models.Model):
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student"
    )
    date = models.DateField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    attendance = models.CharField(
        max_length=10,
        choices=[("Present", "Present"), ("Absent", "Absent"), ("Leave", "Leave")],
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    marked_by = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student} - {self.session} - {self.date}"
