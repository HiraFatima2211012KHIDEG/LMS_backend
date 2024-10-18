from rest_framework import serializers

from ..models.user_models import Student, StudentSession, InstructorSession
from ..models.location_models import City, Batch, Location, Sessions,SessionSchedule
from course.serializers import CourseSerializer
from datetime import datetime, timedelta
from course.models.models import Course,Assignment,Quizzes,Exam,Project


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

class SessionScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionSchedule
        fields = ['day_of_week', 'start_time', 'end_time']


class SessionsSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )
    remaining_spots = serializers.SerializerMethodField()
    session_name = serializers.SerializerMethodField()
    schedules = SessionScheduleSerializer(many=True, write_only=False)

    class Meta:
        model = Sessions
        fields = [
            "id",
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

    def get_session_name(self, obj):
        # Build the custom session name
        return f"{obj.location}-{obj.course}-{obj.no_of_students}-({obj.start_date}-{obj.end_date})"
        
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
    



    def create(self, validated_data):
        # Extract schedules data
        schedules_data = validated_data.pop('schedules')

        # Automatically populate the days_of_week field
        days_of_week = [schedule['day_of_week'] for schedule in schedules_data]
        validated_data['days_of_week'] = days_of_week

        # Create the session instance
        session = super().create(validated_data)

        # Create the schedules for the session
        for schedule_data in schedules_data:
            SessionSchedule.objects.create(session=session, **schedule_data)

        return session

    def update(self, instance, validated_data):
        # Extract schedules data if available
        schedules_data = validated_data.pop('schedules', None)

        # Automatically populate the days_of_week field if schedules are provided
        if schedules_data:
            days_of_week = [schedule['day_of_week'] for schedule in schedules_data]
            validated_data['days_of_week'] = days_of_week

        # Update session instance
        instance = super().update(instance, validated_data)

        # If schedules are provided, update them
        if schedules_data:
            # Clear existing schedules for the session
            instance.schedules.all().delete()

            # Create new schedules
            for schedule_data in schedules_data:
                SessionSchedule.objects.create(session=instance, **schedule_data)

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


class InstructorSessionSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    instructor_id = serializers.IntegerField(source='instructor.id.id')
      
    session = SessionsSerializer()

    class Meta:
        model = InstructorSession
        fields = ['session','instructor_id', 'instructor_name']

    def get_instructor_name(self, obj):
        first_name = obj.instructor.id.first_name
        last_name = obj.instructor.id.last_name
        return f"{first_name} {last_name}".strip()



WEEKDAYS = {
    0: ("Monday", "Mon"),
    1: ("Tuesday", "Tue"),
    2: ("Wednesday", "Wed"),
    3: ("Thursday", "Thu"),
    4: ("Friday", "Fri"),
    5: ("Saturday", "Sat"),
    6: ("Sunday", "Sun"),
}



# class SessionsCalendarSerializer(serializers.ModelSerializer):

#     location_name = serializers.CharField(source="location.name", read_only=True)
#     day_names = serializers.SerializerMethodField()
#     course_id = serializers.IntegerField(source="course.id", read_only=True)
#     course_name = serializers.CharField(source="course.name", read_only=True)
#     dates_with_days = serializers.SerializerMethodField()

#     class Meta:
#         model = Sessions
#         fields = [
#             "id",
#             "start_date",
#             "end_date",
#             "location",
#             "location_name",
#             "no_of_students",
#             "start_time",
#             "end_time",
#             "course_id",
#             "course_name",
#             "days_of_week",
#             "day_names",
#             "dates_with_days",  # New field for dates with days
#             "status",
#         ]

#     def get_day_names(self, obj):
#         """Convert the list of integers to their corresponding day names."""
#         return [WEEKDAYS[day][0] for day in obj.days_of_week if day in WEEKDAYS]

#     def get_dates_with_days(self, obj):
#         """Get the dates corresponding to the days of the week within the program's date range."""
     
#         start_date = obj.start_date
#         end_date = obj.end_date
#         days_of_week = obj.days_of_week
        
#         # Generate the dates based on the start and end date and days of the week
#         return self.get_dates_from_days(start_date, end_date, days_of_week)
        

#     def get_dates_from_days(self, start_date, end_date, days_of_week):
#         """Generate a list of dates based on start and end dates and specified days of the week."""
#         current_date = start_date
#         actual_dates = []

#         # Iterate through each day in the range
#         while current_date <= end_date:
#             if current_date.weekday() in days_of_week:
#                 actual_dates.append(current_date.strftime("%Y-%m-%d"))  # Format as string or datetime as needed
#             current_date += timedelta(days=1)

#         return actual_dates

class SessionsCalendarSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    day_names = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)
    dates_with_days = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()
    quizzes = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    exams = serializers.SerializerMethodField()
    session_times = serializers.SerializerMethodField()  # New field to fetch start/end times

    class Meta:
        model = Sessions
        fields = [
            "id",
            "start_date",
            "end_date",
            "location",
            "location_name",
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

    def get_day_names(self, obj):
        """Convert the list of integers to their corresponding day names."""
        return [WEEKDAYS[day][0] for day in obj.days_of_week if day in WEEKDAYS]

    def get_dates_with_days(self, obj):
        """Get the dates corresponding to the days of the week within the program's date range."""
        start_date = obj.start_date
        end_date = obj.end_date
        days_of_week = obj.days_of_week

        # Generate the dates based on the start and end date and days of the week
        return self.get_dates_from_days(start_date, end_date, days_of_week)

    def get_dates_from_days(self, start_date, end_date, days_of_week):
        """Generate a list of dates based on start and end dates and specified days of the week."""
        current_date = start_date
        actual_dates = []

        # Iterate through each day in the range
        while current_date <= end_date:
            if current_date.weekday() in days_of_week:
                actual_dates.append(
                    current_date.strftime("%Y-%m-%d")
                )  # Format as string or datetime as needed
            current_date += timedelta(days=1)

        return actual_dates

    # New method to get session start/end times from the SessionSchedule model
    def get_session_times(self, obj):
        schedules = obj.schedules.all()
        return [
            {
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time.strftime("%H:%M"),
                "end_time": schedule.end_time.strftime("%H:%M")
            }
            for schedule in schedules
        ]

    # Methods to fetch assessments
    def get_assignments(self, obj):
        assignments = Assignment.objects.filter(
            course=obj.course, due_date__range=[obj.start_date, obj.end_date]
        )
        return [
            {
                "name": assignment.question,
                "due_date": assignment.due_date.strftime("%Y-%m-%d"),  # Extract date
                "due_time": assignment.due_date.strftime("%H:%M"),  # Extract time
            }
            for assignment in assignments
        ]

    def get_quizzes(self, obj):
        quizzes = Quizzes.objects.filter(
            course=obj.course, due_date__range=[obj.start_date, obj.end_date]
        )
        return [
            {
                "name": quiz.question,
                "due_date": quiz.due_date.strftime("%Y-%m-%d"),
                "due_time": quiz.due_date.strftime("%H:%M"),
            }
            for quiz in quizzes
        ]

    def get_projects(self, obj):
        projects = Project.objects.filter(
            course=obj.course, due_date__range=[obj.start_date, obj.end_date]
        )
        return [
            {
                "name": project.title,
                "due_date": project.due_date.strftime("%Y-%m-%d"),
                "due_time": project.due_date.strftime("%H:%M"),
            }
            for project in projects
        ]

    def get_exams(self, obj):
        exams = Exam.objects.filter(
            course=obj.course, due_date__range=[obj.start_date, obj.end_date]
        )
        return [
            {
                "name": exam.title,
                "due_date": exam.due_date.strftime("%Y-%m-%d"),
                "due_time": exam.due_date.strftime("%H:%M"),
            }
            for exam in exams
        ]