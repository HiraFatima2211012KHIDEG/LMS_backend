from rest_framework import filters, views, generics, permissions, status
from rest_framework.response import Response
from django.db.models import Sum
from ..models.location_models import (
    City,
    Batch,
    Location,
    Sessions,
)
from ..models.user_models import Instructor
from utils.custom import BaseLocationViewSet
from ..serializers.location_serializers import (
    CitySerializer,
    BatchSerializer,
    LocationSerializer,
    SessionsSerializer,
    AssignSessionsSerializer,
)
from ..models.user_models import User
from utils.custom import CustomResponseMixin, custom_extend_schema
from drf_spectacular.utils import extend_schema, inline_serializer


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
    filter_backends = [filters.SearchFilter]
    search_fields = ["location__name"]


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

    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

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
        city_name = request.query_params.get("city", None)

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
        city_name = request.query_params.get("city", None)

        if not city_name:
            return Response({"error": "City parameter is required."}, status=400)
        locations = Location.objects.filter(city__iexact=city_name)

        location_serializer = LocationSerializer(locations, many=True)

        return Response({"locations": location_serializer.data})


class FilterSessionsByLocationView(views.APIView):
    """
    API view to filter Sessions by location name (case-insensitive).
    """

    def get(self, request):
        location_name = request.query_params.get("location", None)

        if not location_name:
            return Response({"error": "Location parameter is required."}, status=400)
        sessions = Sessions.objects.filter(location__name__icontains=location_name)
        session_serializer = SessionsSerializer(sessions, many=True)

        return Response({"sessions": session_serializer.data})


class FilterSessionsView(views.APIView):
    """
    API view to filter sessions based on the query parameter: 'student' or 'instructor'.
    """

    def get(self, request):
        user_type = request.query_params.get("user_type", "").lower()

        if user_type not in ["student", "instructor"]:
            return Response(
                {
                    "error": "Query parameter 'user_type' must be either 'student' or 'instructor'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        sessions = Sessions.objects.none()

        if user_type == "student":
            sessions = Sessions.objects.filter(student__isnull=False).distinct()

        elif user_type == "instructor":
            sessions = Sessions.objects.filter(instructor__isnull=False).distinct()
        session_serializer = SessionsSerializer(sessions, many=True)

        return Response(
            {"sessions": session_serializer.data}, status=status.HTTP_200_OK
        )


class CityStatsView(views.APIView, CustomResponseMixin):
    """
    API view to get count of student and instructor users and total capacity for each city.
    """

    def get(self, request):
        try:
            # Fetch all unique cities from User table, excluding null and empty cities
            cities = (
                User.objects.exclude(city__isnull=True)
                .exclude(city__exact="")
                .values_list("city", flat=True)
                .distinct()
            )
            data = []

            for city in cities:
                # Count of student users in the city
                student_count = User.objects.filter(
                    city=city, groups__name="student"
                ).count()
                # Count of instructor users in the city
                instructor_count = User.objects.filter(
                    city=city, groups__name="instructor"
                ).count()

                # Calculate total capacity for each city
                total_capacity = (
                    Location.objects.filter(city=city).aggregate(
                        total_capacity=Sum("capacity")
                    )["total_capacity"]
                    or 0
                )  # Default to 0 if no capacity is found

                # Append the results for each city
                data.append(
                    {
                        "city": city,
                        "student_count": student_count,
                        "instructor_count": instructor_count,
                        "total_capacity": total_capacity,
                    }
                )

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
