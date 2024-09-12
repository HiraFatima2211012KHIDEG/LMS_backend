from rest_framework import viewsets, mixins, status, generics, permissions
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
from utils.custom import CustomResponseMixin, custom_extend_schema
from rest_framework import views
from drf_spectacular.utils import extend_schema, inline_serializer
from django.db.models import Sum
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


class CityViewSet(BaseLocationViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class BatchViewSet(BaseLocationViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer


class LocationViewSet(BaseLocationViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


# class SessionsViewSet(BaseLocationViewSet):
#     queryset = Sessions.objects.all()
#     serializer_class = SessionsSerializer


class SessionsViewSet(viewsets.ModelViewSet):
    queryset = Sessions.objects.all()
    serializer_class = SessionsSerializer

    def perform_create(self, serializer):
        self.validate_session(serializer)
        serializer.save()

    def perform_update(self, serializer):
        self.validate_session(serializer)
        serializer.save()

    def validate_session(self, serializer):
        # Query to check if a session with the same location, course, start_time, and end_time exists
        existing_sessions = Sessions.objects.filter(
            location=serializer.validated_data.get("location"),
            course=serializer.validated_data.get("course"),
            start_time=serializer.validated_data.get("start_time"),
            end_time=serializer.validated_data.get("end_time")
        )

        # If this is an update (i.e., serializer.instance exists), exclude the current session from the query
        if serializer.instance:
            existing_sessions = existing_sessions.exclude(id=serializer.instance.id)

        if existing_sessions.exists():
            raise serializer.ValidationError(
                "A session with the same location, course, start time, and end time already exists."
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except ValidationError as e:
            return Response(
                {"status_code": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"status_code": status.HTTP_201_CREATED, "message": "Session created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except ValidationError as e:
            return Response(
                {"status_code": status.HTTP_400_BAD_REQUEST, "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"status_code": status.HTTP_200_OK, "message": "Session updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
            headers=headers
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



class SessionCalendarAPIView(APIView,CustomResponseMixin):
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
            session_data = SessionsCalendarSerializer(session).data
            for date in session_data['days_of_week']:
                if date not in calendar_data:
                    calendar_data[date] = []

                # Add the session data to the list for the given date
                calendar_data[date].append({
                    "start_time": session_data['start_time'],
                    "end_time": session_data['end_time'],
                    "course_id": session_data['course_id'],
                    "course_name": session_data['course_name'],
                    "location": session_data['location_name'],
                    "batch": session_data['batch']
                })
            print("Calender",calendar_data)
        # Format the data into the required structure
        formatted_data = [
            {
                "date": date,
                "sessions": session_list  # Ensure all sessions for the date are included
            }
            for date, session_list in calendar_data.items()
        ]

        # Sort the formatted data by date
        formatted_data.sort(key=lambda x: x['date'])

        # return Response(formatted_data)
        return self.custom_response(
                status.HTTP_200_OK,
                "Calender data fetched successfully.",
                formatted_data
            )