from rest_framework import status, generics, permissions
from rest_framework.response import Response
from ..models.location_models import *
from ..models.user_models import *
from utils.custom import BaseLocationViewSet
from ..serializers.location_serializers import *
from utils.custom import *
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import views
from drf_spectacular.utils import extend_schema, inline_serializer
from django.db.models import Sum
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from datetime import timedelta, datetime
from ..serializers import UserSerializer
from constants import WEEKDAYS


class BatchViewSet(BaseLocationViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer


class SessionsAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Check if we're fetching a single session by id or filtered sessions
        session_id = kwargs.get("pk", None)

        if session_id:
            # Fetch a single session by id
            session = get_object_or_404(Sessions, id=session_id)
            serializer = SessionsSerializer(session)
            print(serializer.data["location"])
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "Session fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Filter sessions based on query parameters
            queryset = Sessions.objects.filter(status__in=[0, 1])
            print(queryset)
            # Filtering by 'course' if provided in the query parameters
            course_id = request.query_params.get("course")
            if course_id:
                queryset = queryset.filter(course__id=course_id)

            serializer = SessionsSerializer(queryset, many=True)
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "Sessions fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

    def post(self, request, *args, **kwargs):
        data = request.data

        if isinstance(data, list):
            # Handle bulk session creation
            serializer = SessionsSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Sessions created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            # Handle single session creation
            serializer = SessionsSerializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
            except ValidationError as e:
                return Response(
                    {
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": str(e),
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Session created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

    def put(self, request, *args, **kwargs):
        session_id = kwargs.get("pk", None)
        instance = get_object_or_404(Sessions, id=session_id)
        serializer = SessionsSerializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        except ValidationError as e:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": str(e),
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "Session updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        session = serializer.save()

        # Handle session schedules
        schedules_data = serializer.validated_data.get("schedules", [])

        for schedule_data in schedules_data:
            day_of_week = schedule_data["day_of_week"]
            start_time = schedule_data["start_time"]
            end_time = schedule_data["end_time"]

            # Check if a schedule for this session and day_of_week already exists
            schedule_exists = SessionSchedule.objects.filter(
                session=session, day_of_week=day_of_week
            ).exists()

            if not schedule_exists:
                # If no existing schedule, create a new one
                SessionSchedule.objects.create(
                    session=session,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                )
            else:
                # If it exists, update the existing schedule
                schedule = SessionSchedule.objects.get(
                    session=session, day_of_week=day_of_week
                )
                schedule.start_time = start_time
                schedule.end_time = end_time
                schedule.save()

    def perform_update(self, serializer):
        schedules_data = self.request.data.get("schedules", None)
        session = serializer.save()

        if schedules_data:
            # Delete old schedules and recreate new ones
            SessionSchedule.objects.filter(session=session).delete()
            for schedule_data in schedules_data:
                SessionSchedule.objects.create(session=session, **schedule_data)

    def delete(self, request, *args, **kwargs):
        session_id = kwargs.get("pk", None)
        instance = get_object_or_404(Sessions, id=session_id)

        instance.status = 2
        instance.save()

        cascade_status_change(instance, 2)

        return Response(
            {
                "status_code": status.HTTP_204_NO_CONTENT,
                "message": "Session deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class FilterBatchByCityView(views.APIView):
    """
    API view to filter Batches by city.
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="city", description="Filter by batches", required=False, type=str
            )
        ],
        responses={200: "application/json"},
    )
    def get(self, request):
        city_name = request.query_params.get("city", None)

        if not city_name:
            return Response({"error": "City parameter is required."}, status=400)

        batches = Batch.objects.filter(city__iexact=city_name)
        batch_serializer = BatchSerializer(batches, many=True)

        return Response({"batches": batch_serializer.data})


class SessionCalendarAPIView(APIView, CustomResponseMixin):
    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        sessions = []

        try:
            student = Student.objects.get(user=user)
            student_sessions = StudentSession.objects.filter(student=student)
            sessions.extend([ss.session for ss in student_sessions])
        except Student.DoesNotExist:
            try:
                instructor = Instructor.objects.get(id=user)
                instructor_sessions = InstructorSession.objects.filter(
                    instructor=instructor
                )
                sessions.extend([is_.session for is_ in instructor_sessions])
            except Instructor.DoesNotExist:
                return Response(
                    {"detail": "User is neither a student nor an instructor."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if not sessions:
            return Response(
                {"detail": "No sessions found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        calendar_data = {}

        for session in sessions:
            start_date = session.start_date
            end_date = session.end_date
            session_days = session.days_of_week
            actual_dates = self.get_dates_from_days(start_date, end_date, session_days)
            session_data = SessionsCalendarSerializer(session).data

            # Try to get schedules for the session
            schedules = SessionSchedule.objects.filter(session=session)

            if schedules.exists():
                # If schedules exist, process them
                for schedule in schedules:
                    schedule_day = schedule.day_of_week
                    schedule_start_time = schedule.start_time
                    schedule_end_time = schedule.end_time

                    for date in actual_dates:
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        if WEEKDAYS[date_obj.weekday()][0] == schedule_day:
                            if date not in calendar_data:
                                calendar_data[date] = []

                            calendar_data[date].append(
                                {
                                    "start_time": schedule_start_time.strftime("%H:%M"),
                                    "end_time": schedule_end_time.strftime("%H:%M"),
                                    "course_id": session_data.get("course_id", None),
                                    "course_name": session_data.get(
                                        "course_name", "Unknown Course"
                                    ),
                                    "location": session_data.get(
                                        "location_name", "Unknown Location"
                                    ),
                                }
                            )
            else:
                # Log the missing schedules but proceed with assessments
                print(f"No schedules found for session {session.id}")

            # Add assessments even if there are no schedules
            for assessment_type in ["assignments", "quizzes", "projects", "exams"]:
                assessments = session_data.get(assessment_type, [])
                if assessments and isinstance(assessments, list):
                    for assessment in assessments:
                        due_date = assessment.get("due_date")
                        if due_date:
                            if due_date not in calendar_data:
                                calendar_data[due_date] = []
                            calendar_data[due_date].append(
                                {
                                    "assessment_name": assessment.get(
                                        "name", "Unknown Assessment"
                                    ),
                                    "due_time": assessment.get(
                                        "due_time", "Unknown Time"
                                    ),
                                    "course_id": session_data.get("course_id", None),
                                    "course_name": session_data.get(
                                        "course_name", "Unknown Course"
                                    ),
                                    "type": assessment_type.capitalize()[:-1],
                                }
                            )

        if not calendar_data:
            return self.custom_response(
                status.HTTP_200_OK, "No calendar data available.", []
            )

        formatted_data = [
            {
                "date": date,
                "day_name": WEEKDAYS[datetime.strptime(date, "%Y-%m-%d").weekday()][0],
                "sessions": session_list,
            }
            for date, session_list in calendar_data.items()
        ]
        formatted_data.sort(key=lambda x: x["date"])

        return self.custom_response(
            status.HTTP_200_OK, "Calendar data fetched successfully.", formatted_data
        )

    def get_dates_from_days(self, start_date, end_date, days_of_week):
        """Generate a list of dates based on start and end dates and specified days of the week."""
        current_date = start_date
        actual_dates = []

        while current_date <= end_date:
            if current_date.weekday() in days_of_week:
                actual_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        return actual_dates


class FilterUsersByBatchView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        batch_id = self.kwargs["batch_id"]
        try:
            batch = Batch.objects.get(batch=batch_id)

            # Filter users based on created_at date falling within batch's date range
            return User.objects.filter(
                created_at__range=[batch.application_start_date, batch.start_date]
            ).filter(city=batch.city)
        except Batch.DoesNotExist:
            return User.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "No users found for the given batch."},
                status=status.HTTP_404_NOT_FOUND,
            )
