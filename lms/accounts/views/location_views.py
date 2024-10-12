from rest_framework import viewsets, mixins, status, generics, permissions, serializers
from rest_framework.response import Response
from ..models.location_models import (
    City,
    Batch,
    Location,
    Sessions,
)
from ..models.user_models import Instructor, User, Student, StudentSession,InstructorSession
from utils.custom import BaseLocationViewSet
from ..serializers.location_serializers import (
    CitySerializer,
    BatchSerializer,
    LocationSerializer,
    SessionsSerializer,
    AssignSessionsSerializer,
    SessionsCalendarSerializer
)
from utils.custom import CustomResponseMixin, custom_extend_schema, cascade_status_change
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import views
from drf_spectacular.utils import extend_schema, inline_serializer
from django.db.models import Sum
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from datetime import timedelta, datetime

class CityViewSet(BaseLocationViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class BatchViewSet(BaseLocationViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer


class LocationViewSet(BaseLocationViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        location = request.data.get("name")
        short_name = request.data.get("shortname")
        print("data", location, short_name)
        # Check if a Location with the same city and shortname already exists
        if Location.objects.filter(
            name=location, shortname=short_name, status__in=[0, 1]
        ).exists():
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "A location with this name and shortname already exists.",
                None,
            )

        # Proceed with the standard create method if no matching record is found
        response = super().create(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_201_CREATED, "created successfully", response.data
        )


# class SessionsViewSet(BaseLocationViewSet):
#     queryset = Sessions.objects.all()
#     serializer_class = SessionsSerializer



# class SessionsViewSet(viewsets.ModelViewSet):
#     queryset = Sessions.objects.all()
#     serializer_class = SessionsSerializer

#     def perform_create(self, serializer):
#         # Check if this is a bulk creation
#         if isinstance(serializer.validated_data, list):
#             for session_data in serializer.validated_data:
#                 self.validate_session(session_data)
#             serializer.save()  # Save all sessions
#         else:
#             self.validate_session(serializer.validated_data)
#             serializer.save()  # Save single session

#     def perform_update(self, serializer):
#         validated_data = serializer.validated_data
#         print("Validated Data: ", validated_data)  # Debugging: Check the data being updated

#         self.validate_session(serializer.validated_data)
#         serializer.save()

#     def validate_session(self, validated_data):
#         # Query to check if a session with the same location, course, start_time, and end_time exists
#         existing_sessions = Sessions.objects.filter(
#             location=validated_data.get("location"),
#             course=validated_data.get("course"),
#             start_time=validated_data.get("start_time"),
#             end_time=validated_data.get("end_time")
#         )

#         # If this is an update, exclude the current session from the query
#         if 'id' in validated_data:
#             existing_sessions = existing_sessions.exclude(id=validated_data.get('id'))

#         if existing_sessions.exists():
#             raise serializers.ValidationError(
#                 "A session with the same location, course, start time, and end time already exists."
#             )

#     def create(self, request, *args, **kwargs):
#         data = request.data

#         # Check if the request contains a list
#         if isinstance(data, list):
#             # Handle bulk creation of sessions
#             serializer = self.get_serializer(data=data, many=True)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)
#             return Response(
#                 {"status_code": status.HTTP_201_CREATED, "message": "Sessions created successfully.", "data": serializer.data},
#                 status=status.HTTP_201_CREATED,
#                 headers=headers
#             )
#         else:
#             # Handle a single session creation
#             serializer = self.get_serializer(data=data)
#             try:
#                 serializer.is_valid(raise_exception=True)
#                 self.perform_create(serializer)
#             except serializers.ValidationError as e:
#                 return Response(
#                     {"status_code": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": None},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             headers = self.get_success_headers(serializer.data)
#             return Response(
#                 {"status_code": status.HTTP_201_CREATED, "message": "Session created successfully.", "data": serializer.data},
#                 status=status.HTTP_201_CREATED,
#                 headers=headers
#             )

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         print("Request Data: ", request.data)  # Log request data for debugging
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         try:
#             serializer.is_valid(raise_exception=True)
#             print("Validated Data: ", serializer.validated_data)  # Log validated data for debugging
#             self.perform_update(serializer)
#         except serializers.ValidationError as e:
#             print("Validation Error: ", e)  # Log validation errors
#             return Response(
#                 {"status_code": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": None},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         headers = self.get_success_headers(serializer.data)
#         return Response(
#             {"status_code": status.HTTP_200_OK, "message": "Session updated successfully.", "data": serializer.data},
#             status=status.HTTP_200_OK,
#             headers=headers
#         )


class SessionsAPIView(APIView):
    #permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Check if we're fetching a single session by id or filtered sessions
        session_id = kwargs.get('pk', None)

        if session_id:
            # Fetch a single session by id
            session = get_object_or_404(Sessions, id=session_id)
            serializer = SessionsSerializer(session)
            return Response(
                {"status_code": status.HTTP_200_OK, "message": "Session fetched successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            # Filter sessions based on query parameters
            queryset = Sessions.objects.filter(
                status__in=[0, 1]
            )
            print(queryset)
            # Filtering by 'course' if provided in the query parameters
            course_id = request.query_params.get('course')
            if course_id:
                queryset = queryset.filter(course__id=course_id)

            # Add other filters if necessary
            # e.g., filter by date, location, etc.

            serializer = SessionsSerializer(queryset, many=True)
            return Response(
                {"status_code": status.HTTP_200_OK, "message": "Sessions fetched successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )



    def post(self, request, *args, **kwargs):
        data = request.data

        if isinstance(data, list):
            # Handle bulk session creation
            serializer = SessionsSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {"status_code": status.HTTP_201_CREATED, "message": "Sessions created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            # Handle single session creation
            serializer = SessionsSerializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
            except ValidationError as e:
                return Response(
                    {"status_code": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"status_code": status.HTTP_201_CREATED, "message": "Session created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

    def put(self, request, *args, **kwargs):
        session_id = kwargs.get('pk', None)
        instance = get_object_or_404(Sessions, id=session_id)
        serializer = SessionsSerializer(instance, data=request.data, partial=True)
        # if instance.status == 0:
        #     instance.status = 0
        #     instance.save()

        #     # Cascade the status change to related objects
        #     cascade_status_change(instance, 0)



        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        except ValidationError as e:
            return Response(
                {"status_code": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"status_code": status.HTTP_200_OK, "message": "Session updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )


    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def delete(self, request, *args, **kwargs):
        session_id = kwargs.get("pk", None)
        instance = get_object_or_404(Sessions, id=session_id)

        # Set the status of the instance to 2
        instance.status = 2
        instance.save()

        # Cascade the status change to related objects
        cascade_status_change(instance, 2)

        return Response(
            {
                "status_code": status.HTTP_204_NO_CONTENT,
                "message": "Session deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )



class CreateBatchLocationSessionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @extend_schema(
        request=inline_serializer(
            name="BatchLocationSession",
            fields={
                "batch": BatchSerializer(),
                "location": LocationSerializer(),
                "session": SessionsSerializer(),
            },
        ),
        responses={
            200: "Successful.",
            400: "Bad Request.",
            401: "Unauthorized.",
        },
        description="Create or get Batch, Location, and Session in a single API call.",
    )
    def post(self, request, *args, **kwargs):
        batch = request.data.get("batch")
        location = request.data.get("location")

        try:
            batch = Batch.objects.get(batch=batch)
        except Batch.DoesNotExist:
            return Response(
                {"detail": "Batch not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            location = Location.objects.get(id=location)
        except Location.DoesNotExist:
            return Response(
                {"detail": "Location not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        session_data = request.data.get("session")
        session_data["location"] = location.id
        session_data["batch"] = batch.batch
        session_serializer = SessionsSerializer(data=session_data)
        if session_serializer.is_valid():
            session_serializer.save()
        else:
            return Response(
                session_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "batch": BatchSerializer(batch).data,
                "location": LocationSerializer(location).data,
                "session": session_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class AssignSessionsView(CustomResponseMixin, views.APIView):
    """Assign sessions to an instructor by providing a list of session IDs."""

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @custom_extend_schema(AssignSessionsSerializer)
    def post(self, request, instructor_id):
        serializer = AssignSessionsSerializer(data=request.data)
        if serializer.is_valid():
            session_ids = serializer.validated_data["session_ids"]
            instructor = Instructor.objects.get(id=instructor_id)
            sessions = Sessions.objects.filter(id__in=session_ids)
            instructor.session.set(sessions)
            return self.custom_response(
                status.HTTP_200_OK, "Sessions assigned successfully.", {}
            )
        return self.custom_response(
            status.HTTP_400_BAD_REQUEST, "Invalid session IDs.", serializer.errors
        )

class FilterBatchByCityView(views.APIView):
    """
    API view to filter Batches by city.
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(name='city', description='Filter by batches', required=False, type=str)
        ],
        responses={200: 'application/json'}
    )

    def get(self, request):
        city_name = request.query_params.get('city', None)

        if not city_name:
            return Response({"error": "City parameter is required."}, status=400)

        batches = Batch.objects.filter(city__iexact=city_name)
        batch_serializer = BatchSerializer(batches, many=True)

        return Response({"batches": batch_serializer.data})


class FilterLocationByCityView(views.APIView):
    """
    API view to filter Locations by city.
    """
    def get(self, request):
        city_name = request.query_params.get('city', None)

        if not city_name:
            return Response({"error": "City parameter is required."}, status=400)
        locations = Location.objects.filter(city__iexact=city_name)

        location_serializer = LocationSerializer(locations, many=True)

        return Response({"locations": location_serializer.data})



# class CityCapacityByLocationView(views.APIView, CustomResponseMixin):
#     """
#     API view to check student capacity for each city.
#     """

#     def get(self, request):
#         try:
#             # Aggregate capacities of locations grouped by city
#             cities_with_capacity = (
#                 City.objects
#                 .annotate(total_capacity=Sum('location__capacity'))  # Assuming 'location' is the related_name from Location to City
#             )

#             # Create a dictionary with city names and their respective capacities
#             total_city_capacity = {
#                 city.name: city.total_capacity or 0  # Handle None values by converting them to 0
#                 for city in cities_with_capacity
#             }

#             # Return the successful response with city capacities
#             return self.custom_response(
#                 status.HTTP_200_OK,
#                 "Data fetched successfully.",
#                 total_city_capacity
#             )

#         except Exception as e:
#             # Handle unexpected errors and log if necessary
#             return self.custom_response(
#                 status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 f"An error occurred: {str(e)}",
#                 None
#             )




# class UserCountByCityView(views.APIView, CustomResponseMixin):
#     """
#     API view to get count of student and instructor users in each city.
#     """

#     def get(self, request):
#         try:
#             # Fetch all unique cities from User table, excluding null and empty cities
#             cities = User.objects.exclude(city__isnull=True).exclude(city__exact='').values_list('city', flat=True).distinct()
#             data = []

#             for city in cities:
#                 # Count of student users in the city
#                 student_count = User.objects.filter(city=city, groups__name='student').count()
#                 # Count of instructor users in the city
#                 instructor_count = User.objects.filter(city=city, groups__name='instructor').count()

#                 # Append the results for each city
#                 data.append({
#                     'city': city,
#                     'student_count': student_count,
#                     'instructor_count': instructor_count
#                 })

#             return self.custom_response(
#                 status.HTTP_200_OK,
#                 "Data fetched successfully.",
#                 data
#             )

#         except Exception as e:
#             # Handle unexpected errors
#             return self.custom_response(
#                 status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 f"An error occurred: {str(e)}",
#                 None
#             )


# class CityCapacityView(views.APIView, CustomResponseMixin):
#     """
#     API view to get the total capacity for each city based on locations.
#     """

#     def get(self, request):
#         try:
#             # Fetch all unique cities from Location table, excluding null and empty cities
#             cities = (
#                 Location.objects.exclude(city__isnull=True)
#                 .exclude(city__exact="")
#                 .values_list("city", flat=True)
#                 .distinct()
#             )

#             data = []

#             # Calculate total capacity for each city
#             for city in cities:
#                 total_capacity = Location.objects.filter(city=city).aggregate(
#                     total_capacity=Sum("capacity")
#                 )["total_capacity"] or 0  # Default to 0 if no capacity is found

#                 # Append the city and its total capacity to the response data
#                 data.append({"city": city, "total_capacity": total_capacity})

#             # Return the successful response with data
#             return self.custom_response(
#                 status.HTTP_200_OK, "Data fetched successfully.", data
#             )

#         except Exception as e:
#             # Handle unexpected errors
#             return self.custom_response(
#                 status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 f"An error occurred: {str(e)}",
#                 None,
#             )


class CityStatsView(views.APIView, CustomResponseMixin):
    """
    API view to get count of student and instructor users and total capacity for each city.
    """

    def get(self, request):
        try:
            # Fetch all unique cities from User table, excluding null and empty cities
            cities = User.objects.exclude(city__isnull=True).exclude(city__exact='').values_list('city', flat=True).distinct()
            data = []

            for city in cities:
                # Count of student users in the city
                student_count = User.objects.filter(city=city, groups__name='student').count()
                # Count of instructor users in the city
                instructor_count = User.objects.filter(city=city, groups__name='instructor').count()

                # Calculate total capacity for each city
                total_capacity = Location.objects.filter(city=city).aggregate(
                    total_capacity=Sum("capacity")
                )["total_capacity"] or 0  # Default to 0 if no capacity is found

                # Append the results for each city
                data.append({
                    'city': city,
                    'student_count': student_count,
                    'instructor_count': instructor_count,
                    'total_capacity': total_capacity
                })

            return self.custom_response(
                status.HTTP_200_OK,
                "Data fetched successfully.",
                data
            )

        except Exception as e:
            # Handle unexpected errors
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred: {str(e)}",
                None
            )




WEEKDAYS = {
    0: ("Monday", "Mon"),
    1: ("Tuesday", "Tue"),
    2: ("Wednesday", "Wed"),
    3: ("Thursday", "Thu"),
    4: ("Friday", "Fri"),
    5: ("Saturday", "Sat"),
    6: ("Sunday", "Sun"),
}
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
                instructor_sessions = InstructorSession.objects.filter(instructor=instructor)
                sessions.extend([is_.session for is_ in instructor_sessions])
            except Instructor.DoesNotExist:
                return Response({"detail": "User is neither a student nor an instructor."}, status=status.HTTP_404_NOT_FOUND)

        if not sessions:
            return Response({"detail": "No sessions found for this user."}, status=status.HTTP_404_NOT_FOUND)

        calendar_data = {}

        # Iterate over sessions and process each one
        for session in sessions:
            # Directly use session's start and end date
            start_date = session.start_date
            end_date = session.end_date

            # Generate the actual dates based on days of the week
            session_days = session.days_of_week
            actual_dates = self.get_dates_from_days(start_date, end_date, session_days)

            session_data = SessionsCalendarSerializer(session).data

            for date in actual_dates:
                if date not in calendar_data:
                    calendar_data[date] = []

                # Add the session data to the list for the given date
                calendar_data[date].append({
                    "start_time": session_data['start_time'],
                    "end_time": session_data['end_time'],
                    "course_id": session_data['course_id'],
                    "course_name": session_data['course_name'],
                    "location": session_data['location_name'],
                    # "day_name": day_name  # If needed, you can still add the day name here
                })

        # Format the data into the required structure
        formatted_data = [
            {
                "date": date,
                "day_name": WEEKDAYS[datetime.strptime(date, "%Y-%m-%d").weekday()][0],  # Get the day name
                "sessions": session_list
            }
            for date, session_list in calendar_data.items()
        ]

        # Sort the formatted data by date
        formatted_data.sort(key=lambda x: x['date'])

        return self.custom_response(
            status.HTTP_200_OK,
            "Calendar data fetched successfully.",
            formatted_data
        )

    def get_dates_from_days(self, start_date, end_date, days_of_week):
        """Generate a list of dates based on start and end dates and specified days of the week."""
        current_date = start_date
        actual_dates = []

        # Iterate through each day in the range
        while current_date <= end_date:
            if current_date.weekday() in days_of_week:
                actual_dates.append(current_date.strftime("%Y-%m-%d"))  # Format as string or datetime as needed
            current_date += timedelta(days=1)

        return actual_dates





