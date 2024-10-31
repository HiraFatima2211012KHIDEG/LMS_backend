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

    def update(self, request, *args, **kwargs):
        # Retrieve the current instance of Batch
        batch = self.get_object()
        print(batch)
        original_status = batch.status
        new_status = request.data.get("status", original_status)

        response = super().update(request, *args, **kwargs)

        # Check if the status is changing to 0
        if original_status != 0 and new_status == 0:
            with transaction.atomic():
                # Get all students related to this batch and update their users' is_active field
                students_in_batch = Student.objects.filter(
                    registration_id__startswith=batch, status=1
                )

                # Update the is_active field in the related User records
                User.objects.filter(id__in=students_in_batch.values("user_id")).update(
                    is_active=False
                )
                students_in_batch.update(status=2)

                student_sessions = StudentSession.objects.filter(
                    student__in=students_in_batch
                )
                student_sessions.update(status=2)
                sessions = Sessions.objects.filter(batch=batch, status=1)

                sessions.update(status=2)
                student_sessions = StudentSession.objects.filter(
                    session_id__in=sessions
                )
                student_sessions.update(status=2)
                instructor_sessions = InstructorSession.objects.filter(
                    session_id__in=sessions
                )
                instructor_sessions.update(status=2)

        elif original_status != 1 and new_status == 1:
            with transaction.atomic():
                # Get all students related to this batch and update their users' is_active field
                students_in_batch = Student.objects.filter(
                    registration_id__startswith=batch, status=2
                )

                # Update the is_active field in the related User records
                User.objects.filter(id__in=students_in_batch.values("user_id")).update(
                    is_active=True
                )
                students_in_batch.update(status=1)

                student_sessions = StudentSession.objects.filter(
                    student__in=students_in_batch
                )
                student_sessions.update(status=1)
                sessions = Sessions.objects.filter(batch=batch, status=2)

                sessions.update(status=1)
                student_sessions = StudentSession.objects.filter(
                    session_id__in=sessions
                )
                student_sessions.update(status=1)
                instructor_sessions = InstructorSession.objects.filter(
                    session_id__in=sessions
                )
                instructor_sessions.update(status=1)

        return self.custom_response(
            status.HTTP_200_OK, "updated successfully", response.data
        )


class SessionsAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Check if we're fetching a single session by id or filtered sessions
        session_id = kwargs.get("pk", None)

        if session_id:
            # Fetch a single session by id
            session = get_object_or_404(Sessions, id=session_id)
            serializer = SessionsSerializer(session)
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
        print("user", user)
        sessions = []

        try:
            student = Student.objects.get(user=user)
            student_sessions = StudentSession.objects.filter(student=student, status=1)
            sessions.extend([ss.session for ss in student_sessions])
            print(sessions), sessions
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

        # if not sessions:
        #     return Response({"detail": "No sessions found for this user."}, status=status.HTTP_404_NOT_FOUND)

        calendar_data = {}

        # Iterate over sessions and process each one
        for session in sessions:
            # Directly use session's start and end date
            start_date = session.start_date
            end_date = session.end_date

            # Generate the actual dates based on days of the week
            session_days = session.days_of_week
            days_of_week_int = [
                day_num
                for day_num, names in WEEKDAYS.items()
                if any(day in names for day in session_days)
            ]
            actual_dates = self.get_dates_from_days(
                start_date, end_date, days_of_week_int
            )
            print(actual_dates)
            session_data = SessionsCalendarSerializer(session).data
            print("sessions data", session_data)
            for date in actual_dates:
                print("date here", date)
                if date not in calendar_data:
                    calendar_data[date] = []
                print(session_data["session_times"][0].get("start_time"))
                # Add the session data to the list for the given date
                calendar_data[date].append(
                    {
                        "start_time": session_data["session_times"][0].get(
                            "start_time"
                        ),
                        "end_time": session_data["session_times"][0].get("end_time"),
                        "course_id": session_data["course_id"],
                        "course_name": session_data["course_name"],
                        "location": session_data["location"],
                        # "day_name": day_name  # If needed, you can still add the day name here
                    }
                )
                print(calendar_data)

        # Format the data into the required structure
        formatted_data = [
            {
                "date": date,
                "day_name": WEEKDAYS[datetime.strptime(date, "%Y-%m-%d").weekday()][
                    0
                ],  # Get the day name
                "sessions": session_list,
            }
            for date, session_list in calendar_data.items()
        ]

        # Sort the formatted data by date
        formatted_data.sort(key=lambda x: x["date"])

        return self.custom_response(
            status.HTTP_200_OK, "Calendar data fetched successfully.", formatted_data
        )

    def get_dates_from_days(self, start_date, end_date, days_of_week):
        """Generate a list of dates based on start and end dates and specified days of the week."""
        current_date = start_date
        actual_dates = []
        print("here")
        # Iterate through each day in the range
        while current_date <= end_date:
            print("inside wile loop")
            print("sndaksn", current_date.weekday(), days_of_week)
            if current_date.weekday() in days_of_week:
                print("current date", current_date)
                actual_dates.append(
                    current_date.strftime("%Y-%m-%d")
                )  # Format as string or datetime as needed
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
                created_at__range=[batch.application_start_date, batch.start_date],
                is_active=True,
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


class BatchStatsView(views.APIView, CustomResponseMixin):
    """
    API view to get count of student and instructor users, total capacity,
    and detailed location-based stats for each batch.
    """

    def get(self, request):
        try:
            batches = Batch.objects.all()
            data = []

            for batch in batches:
                batch_data = {
                    "batch": batch.batch,  # Assuming 'batch' is the batch identifier
                    "locations": [],
                }
                print(batch)

                # Get all locations associated with sessions in the batch
                locations_in_batch = (
                    Sessions.objects.filter(batch=batch, status=1)
                    .values_list("location", flat=True)
                    .distinct()
                )
                print(locations_in_batch)
                # Loop through each location and gather stats for that location within the batch
                for location in locations_in_batch:
                    # Count students associated with this batch and location
                    student_count = Student.objects.filter(
                        registration_id__startswith=batch,
                        studentsession__session__location=location,
                        status=1,
                    ).count()
                    print(student_count)

                    # Count instructors associated with this batch and location
                    # instructor_ids = (
                    #     StudentSession.objects.filter(
                    #         session__batch=batch,
                    #         session__location__name=location_name
                    #     )
                    #     .values_list("instructor__id", flat=True)
                    #     .distinct()
                    # )
                    # instructor_count = len(instructor_ids)

                    # Calculate total capacity for this location within the batch
                    total_capacity = (
                        Sessions.objects.filter(
                            batch=batch, location=location, status=1
                        ).aggregate(total_capacity=Sum("no_of_students"))[
                            "total_capacity"
                        ]
                        or 0
                    )
                    print(total_capacity)

                    # Add location-specific data to batch data
                    batch_data["locations"].append(
                        {
                            "location_name": location,
                            "student_count": student_count,
                            # "instructor_count": instructor_count,
                            "total_capacity": total_capacity,
                        }
                    )

                # Append batch data to main data list
                data.append(batch_data)

            return self.custom_response(
                status.HTTP_200_OK, "Data fetched successfully.", data
            )

        except Exception as e:
            # Handle unexpected errors
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred: {str(e)}",
                None,
            )
