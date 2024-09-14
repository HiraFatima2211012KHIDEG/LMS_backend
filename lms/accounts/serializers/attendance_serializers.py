from rest_framework import serializers
from ..models.attendance_models import Attendance


# class AttendanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Attendance
#         fields = ["id", "session", "student","course", "date", "status", "marked_by"]

class BulkAttendanceSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        attendances = [Attendance(**item) for item in validated_data]
        return Attendance.objects.bulk_create(attendances)

class AttendanceSerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ["id", "student", "student_name", "course", "date", "status", "marked_by", "day"]
        list_serializer_class = BulkAttendanceSerializer

    def get_day(self, obj):
        return obj.date.strftime('%A')

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"



# class AttendanceSerializer(serializers.ModelSerializer):
#     day = serializers.SerializerMethodField()
#     student_name = serializers.SerializerMethodField()

#     class Meta:
#         model = Attendance
#         fields = ["id", "student","student_name", "course", "date", "status", "marked_by", "day"]

#     def get_day(self, obj):
#         return obj.date.strftime('%A')

#     def get_student_name(self, obj):
#         return f"{obj.student.user.first_name} {obj.student.user.last_name}"