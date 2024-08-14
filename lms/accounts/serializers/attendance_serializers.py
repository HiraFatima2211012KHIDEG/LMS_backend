from rest_framework import serializers
from ..models.attendance_models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "session", "student","course", "date", "status", "marked_by"]
