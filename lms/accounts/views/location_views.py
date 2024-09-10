from rest_framework import viewsets, mixins, status, generics, permissions
from rest_framework.response import Response
from ..models.location_models import (
    City,
    Batch,
    Location,
    Sessions,
)
from ..models.user_models import Instructor, User, Student
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


class CityViewSet(BaseLocationViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class BatchViewSet(BaseLocationViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer


class LocationViewSet(BaseLocationViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class SessionsViewSet(BaseLocationViewSet):
    queryset = Sessions.objects.all()
    serializer_class = SessionsSerializer


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



class SessionCalendarAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch all sessions
        sessions = Sessions.objects.all()
        # Prepare the response data
        data = {}
        for session in sessions:
            session_data = SessionsCalendarSerializer(session).data
            days_of_week = session_data['days_of_week']
            day_names = session_data['day_names']
            # Populate the response dictionary
            for i, day in enumerate(days_of_week):
                if day not in data:
                    data[day] = {
                        "start_time": session_data['start_time'],
                        "end_time": session_data['end_time'],
                        "day_names": [day_names[i]],
                        "course_id": session_data['course_id'],
                        "course_name": session_data['course_name']
                    }
                else:
                    # If day already exists, append the new day name
                    data[day]["day_names"].append(day_names[i])
        # Format the data into the required structure
        formatted_data = []
        for day, details in data.items():
            formatted_data.append({
                "days_of_week": day,
                **details
            })
        return Response(formatted_data)