from rest_framework import serializers

from ..models.user_models import Student, StudentSession, InstructorSession
from ..models.location_models import City, Batch, Location, Sessions
from course.serializers import CourseSerializer
from datetime import datetime
from course.models.models import Course


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
            "term",
            "created_at"
        ]

class LocationSerializer(serializers.ModelSerializer):
    remaining_spots_for_location = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ["id", "name", "shortname", "capacity", "city", "status", "remaining_spots_for_location","created_at"]

    def get_remaining_spots_for_location(self, obj):
        # Assuming there is a relationship between Location and Sessions or StudentSession
        total_students_assigned = StudentSession.objects.filter(session__location=obj).count()
        remaining_spots = obj.capacity - total_students_assigned
        return max(remaining_spots, 0)  # Ensure it never goes negative

    def validate(self, data):
        # Check if this is an update (self.instance is not None) or create (self.instance is None)
        location = self.instance

        # If this is an update, proceed with remaining spots validation
        if location:
            total_students_assigned = StudentSession.objects.filter(session__location=location).count()
            remaining_spots = location.capacity - total_students_assigned

            if remaining_spots <= 0:
                raise serializers.ValidationError(f"No remaining spots in location {location.name}. Cannot assign more students.")
        
        # For create requests, ensure the capacity is provided
        elif 'capacity' in data:
            # Perform any additional validation during creation if needed
            capacity = data['capacity']
            if capacity <= 0:
                raise serializers.ValidationError("Capacity must be greater than 0.")
        
        return data

class SessionsSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )
    remaining_spots = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()

    class Meta:
        model = Sessions
        fields = [
            "id",
            "location",
            "location_name",
            "no_of_students",
            "remaining_spots",
            "start_time",
            "end_time",
            "days_of_week",
            "status",
            "course",
            "course_id",
            "session_name", 
            "created_at"
        ]

    def get_session_name(self, obj):
        # Build the custom session name
        return f"{obj.location}-{obj.course}-{obj.no_of_students}-({obj.start_time}-{obj.end_time})"
        
    def get_remaining_spots(self, obj):
        assigned_students = StudentSession.objects.filter(session=obj).count()
        remaining_spots = obj.no_of_students - assigned_students

        # Prevent negative remaining spots
        if remaining_spots < 0:
            remaining_spots = 0

        return remaining_spots

    def validate(self, data):
        session = self.instance

        if session:
            assigned_students = StudentSession.objects.filter(session=session).count()
            remaining_spots = session.no_of_students - assigned_students

            if remaining_spots <= 0:
                raise serializers.ValidationError(
                    "The session is already full. No more students can be assigned."
                )

        return data

    def update(self, instance, validated_data):

        assigned_students = StudentSession.objects.filter(session=instance).count()
        instance.no_of_students = instance.no_of_students - assigned_students
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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
        fields = ["session_id", "instructor_email", "status", "start_date", "end_date"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure to include only serializable fields
        representation["instructor_email"] = instance.instructor.id  # Email as string
        return representation


WEEKDAYS = {
    0: ("Monday", "Mon"),
    1: ("Tuesday", "Tue"),
    2: ("Wednesday", "Wed"),
    3: ("Thursday", "Thu"),
    4: ("Friday", "Fri"),
    5: ("Saturday", "Sat"),
    6: ("Sunday", "Sun"),
}


class SessionsCalendarSerializer(serializers.ModelSerializer):
    batch_start_date = serializers.DateField(source="batch.start_date", read_only=True)
    batch_end_date = serializers.DateField(source="batch.end_date", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    # weekdays = serializers.SerializerMethodField()
    day_names = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(
        source="course.id", read_only=True
    )  # Include course ID
    course_name = serializers.CharField(
        source="course.name", read_only=True
    )  # Include course name

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
        return [
            WEEKDAYS[datetime.strptime(day, "%Y-%m-%d").weekday()]
            for day in obj.days_of_week
        ]
