from rest_framework import serializers
from ..models.user_models import StudentSession, InstructorSession
from ..models.location_models import Batch, Sessions, SessionSchedule
from course.serializers import CourseSerializer
from course.models.models import Course, Assignment, Quizzes, Exam, Project
from constants import WEEKDAYS
from datetime import timedelta
from utils.custom import get_assessment
from constants import ROOMS


class BatchSerializer(serializers.ModelSerializer):
    batch = serializers.CharField(read_only=True)

    class Meta:
        model = Batch
        fields = [
            "batch",
            "name",
            "short_name",
            "year",
            "no_of_students",
            "application_start_date",
            "application_end_date",
            "start_date",
            "end_date",
            "status",
            "created_at",
        ]

    def get_remaining_slots_for_batch(self, obj):
        session = Sessions.objects.filter(Batch=obj)
        total_students_assigned = StudentSession.objects.filter(session=session).count()
        remaining_spots = obj.capacity - total_students_assigned
        return max(remaining_spots, 0)

    def validate(self, data):
        session = self.instance  # Current session instance

        if session:
            total_students_assigned = StudentSession.objects.filter(session=session).count()

            remaining_spots = session.capacity - total_students_assigned

            if remaining_spots <= 0:
                raise serializers.ValidationError(
                    f"No remaining spots in session {session.id}. Cannot assign more students."
                )
        elif "capacity" in data:
            capacity = data["capacity"]
            if capacity <= 0:
                raise serializers.ValidationError("Capacity must be greater than 0.")

        return data


class SessionScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionSchedule
        fields = ["day_of_week", "start_time", "end_time"]


class SessionsSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )
    remaining_spots = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    schedules = SessionScheduleSerializer(many=True, write_only=False)

    class Meta:
        model = Sessions
        fields = [
            "id",
            "batch",
            "location",
            "location_name",
            "no_of_students",
            "remaining_spots",
            "start_date",
            "end_date",
            "days_of_week",
            "status",
            "course",
            "course_id",
            "session_name",
            "created_at",
            "schedules",
        ]

    def get_location_name(self, obj):
        # Retrieve the name of the location from ROOMS dictionary
        return ROOMS.get(obj.location, "Unknown")

    def get_session_name(self, obj):
        return f"{obj.location}-{obj.course}-{obj.no_of_students}-({obj.start_date}-{obj.end_date})"

    def get_remaining_spots(self, obj):
        assigned_students = StudentSession.objects.filter(session=obj).count()
        remaining_spots = obj.no_of_students - assigned_students
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

    def create(self, validated_data):
        schedules_data = validated_data.pop("schedules")
        days_of_week = [schedule["day_of_week"] for schedule in schedules_data]
        validated_data["days_of_week"] = days_of_week
        session = super().create(validated_data)
        for schedule_data in schedules_data:
            SessionSchedule.objects.create(session=session, **schedule_data)

        return session

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop("schedules", None)
        if schedules_data:
            days_of_week = [schedule["day_of_week"] for schedule in schedules_data]
            validated_data["days_of_week"] = days_of_week
        instance = super().update(instance, validated_data)
        if schedules_data:
            instance.schedules.all().delete()
            for schedule_data in schedules_data:
                SessionSchedule.objects.create(session=instance, **schedule_data)
        return instance


class StudentSessionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentSession
        fields = "__all__"


class InstructorSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorSession
        fields = ["session_id", "instructor_email", "status", "start_date", "end_date"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["instructor_email"] = instance.instructor.id
        return representation


class InstructorSessionSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    instructor_id = serializers.IntegerField(source="instructor.id.id")
    session = SessionsSerializer()

    class Meta:
        model = InstructorSession
        fields = ["session", "instructor_id", "instructor_name"]

    def get_instructor_name(self, obj):
        first_name = obj.instructor.id.first_name
        last_name = obj.instructor.id.last_name
        return f"{first_name} {last_name}".strip()


class SessionsCalendarSerializer(serializers.ModelSerializer):
    day_names = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)
    dates_with_days = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()
    quizzes = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    exams = serializers.SerializerMethodField()
    session_times = serializers.SerializerMethodField()

    class Meta:
        model = Sessions
        fields = [
            "id",
            "start_date",
            "end_date",
            "location",
            "no_of_students",
            "course_id",
            "course_name",
            "days_of_week",
            "day_names",
            "dates_with_days",
            "status",
            "assignments",
            "quizzes",
            "projects",
            "exams",
            "session_times",
        ]

    def get_dates_with_days(self, obj):
        """Get the dates corresponding to the days of the week within the program's date range."""
        start_date = obj.start_date
        end_date = obj.end_date
        days_of_week = obj.days_of_week
        return self.get_dates_from_days(start_date, end_date, days_of_week)

    def get_dates_from_days(self, start_date, end_date, days_of_week):
        """Generate a list of dates based on start and end dates and specified days of the week."""
        current_date = start_date
        actual_dates = []
        while current_date <= end_date:
            if current_date.weekday() in days_of_week:
                actual_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        return actual_dates

    def get_day_names(self, obj):
        """Convert the list of integers to their corresponding day names."""
        return [WEEKDAYS[day][0] for day in obj.days_of_week if day in WEEKDAYS]

    def get_session_times(self, obj):
        schedules = obj.schedules.all()
        return [
            {
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time.strftime("%H:%M"),
                "end_time": schedule.end_time.strftime("%H:%M"),
            }
            for schedule in schedules
        ]

    def get_assignments(self, obj):
        get_assessment(self, obj, Assignment)

    def get_quizzes(self, obj):
        get_assessment(self, obj, Quizzes)

    def get_projects(self, obj):
        get_assessment(self, obj, Project)

    def get_exams(self, obj):
        get_assessment(self, obj, Exam)
