from django.db import models
from django.conf import settings
from .location_models import Sessions
from .user_models import StudentInstructor


class Attendance(models.Model):
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentInstructor, on_delete=models.CASCADE, related_name='student')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[("Present", "Present"), ("Absent", "Absent"), ("Leave", "Leave")],
    )
    marked_by = models.ForeignKey(StudentInstructor, on_delete=models.CASCADE, null=True, related_name='instructor')

    class Meta:
        unique_together = ('session', 'student', 'date')

    def __str__(self):
        return f"{self.student} - {self.session} - {self.date}"
