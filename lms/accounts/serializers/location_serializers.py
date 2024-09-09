from rest_framework import serializers

from ..models.user_models import Student, StudentSession, InstructorSession
from ..models.location_models import City, Batch, Location, Sessions
from course.serializers import CourseSerializer


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
    course = CourseSerializer(read_only=True) 


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
