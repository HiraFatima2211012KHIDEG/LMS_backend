from rest_framework import serializers
from ..models.attendance_models import Attendance
from ..models.user_models import StudentSession
from datetime import datetime


class BulkAttendanceSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        attendances = [Attendance(**item) for item in validated_data]
        return Attendance.objects.bulk_create(attendances)


class AttendanceSerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    class Meta:
        model = Attendance
        fields = [
            "id",
            "student",
            "student_name",
            "course",
            "date",
            "status",
            "marked_by",
            "day",
        ]
        list_serializer_class = BulkAttendanceSerializer
    def get_day(self, obj):
        # Check if obj.date is a string and convert it to a date object
        if isinstance(obj.date, str):
            try:
                obj_date = datetime.strptime(obj.date, "%Y-%m-%d").date()
            except ValueError:
                return None  
        else:
            obj_date = obj.date

        return obj_date.strftime("%A")
    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class StudentDetailAttendanceSerializer(serializers.ModelSerializer):
    registration_id = serializers.CharField(source='student.registration_id')
    user = serializers.SerializerMethodField()
    class Meta:
        model = StudentSession
        fields = ['registration_id', 'user']
    def get_user(self, obj):
        first_name = obj.student.user.first_name
        last_name = obj.student.user.last_name
        return f"{first_name} {last_name}".strip()
