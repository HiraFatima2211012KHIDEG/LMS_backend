from rest_framework import serializers

from ..models.user_models import Student, StudentSession, InstructorSession
from ..models.location_models import City, Batch, Location, Sessions
from course.serializers import CourseSerializer
from datetime import datetime


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["city", "shortname"]


class BatchSerializer(serializers.ModelSerializer):
    batch = serializers.CharField(read_only=True)

    class Meta:
        model = Batch
        fields = [
            "batch",
            "city",
            "city_abb",
            "year",
            "no_of_students",
            "start_date",
            "end_date",
            "status",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "shortname", "capacity", "city", "status"]


class SessionsSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    course = CourseSerializer() 
    class Meta:
        model = Sessions

        fields = [
            "id",
            "location",
            "location_name",
            "no_of_students",
            "batch",
            "start_time",
            "end_time",
            "status",
            "course"
        ]

class StudentSessionsSerializer(serializers.ModelSerializer):

        class Meta:
            model = StudentSession
            fields = "__all__"

class AssignSessionsSerializer(serializers.Serializer):
    session_ids = serializers.ListField(child=serializers.IntegerField())

    def validate_session_ids(self, value):
        # Ensure all session IDs are valid
        if not Sessions.objects.filter(id__in=value).exists():
            raise serializers.ValidationError("Some session IDs are invalid.")
        return value

class InstructorSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorSession
        fields = ['session_id', 'instructor_email', 'status', 'start_date', 'end_date']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure to include only serializable fields
        representation['instructor_email'] = instance.instructor.id  # Email as string
        return representation


WEEKDAYS = {
    0: ('Monday', 'Mon'),
    1: ('Tuesday', 'Tue'),
    2: ('Wednesday', 'Wed'),
    3: ('Thursday', 'Thu'),
    4: ('Friday', 'Fri'),
    5: ('Saturday', 'Sat'),
    6: ('Sunday', 'Sun'),
}
class SessionsCalendarSerializer(serializers.ModelSerializer):
    batch_start_date = serializers.DateField(source="batch.start_date", read_only=True)
    batch_end_date = serializers.DateField(source="batch.end_date", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    # weekdays = serializers.SerializerMethodField()
    day_names = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(source='course.id', read_only=True)  # Include course ID
    course_name = serializers.CharField(source='course.name', read_only=True)  # Include course name

    class Meta:
        model = Sessions
        fields = [
            "id",
            "batch",
            "batch_start_date",
            "batch_end_date",
            "location",
            "location_name",
            "no_of_students",
            "start_time",
            "end_time",
            "course_id",
            "course_name",
            "days_of_week",
            "day_names",
            "status",
        ]
    def get_weekdays(self, obj):
        # Assuming obj.days_of_week contains integers (0-6)
        return [WEEKDAYS[day][1] for day in obj.days_of_week]
    def get_day_names(self, obj):
        """Convert the list of dates to a list of day names."""
        return [WEEKDAYS[datetime.strptime(day, '%Y-%m-%d').weekday()] for day in obj.days_of_week]
        