from rest_framework import serializers
from ..models.attendance_models import Attendance


# class AttendanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Attendance
#         fields = ["id", "session", "student","course", "date", "status", "marked_by"]

class AttendanceSerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ["id", "session", "student", "course", "date", "status", "marked_by", "day"]

    def get_day(self, obj):
        return obj.date.strftime('%A') 