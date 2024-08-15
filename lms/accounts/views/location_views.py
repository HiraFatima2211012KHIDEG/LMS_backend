from rest_framework import viewsets, mixins, status, generics, permissions
from rest_framework.response import Response
from ..models.location_models import (
    City,
    Batch,
    Location,
    Sessions,
)
from ..models.user_models import Student
from ..serializers.location_serializers import (
    CitySerializer,
    BatchSerializer,
    LocationSerializer,
    SessionsSerializer,
    # StudentInstructorSerializer
    StudentSerializer,
)


class CustomResponseMixin:
    def custom_response(self, status_code, message, data):
        return Response(
            {"status_code": status_code, "message": message, "data": data},
            status=status_code,
        )


class BaseLocationViewSet(
    CustomResponseMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    # permission_classes = [permissions.IsAuthenticated]
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_201_CREATED, "created successfully", response.data
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_200_OK, "updated successfully", response.data
        )

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_204_NO_CONTENT, "deleted successfully", None
        )


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
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_201_CREATED, "Session created successfully", response.data
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_200_OK, "Session updated successfully", response.data
        )

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_204_NO_CONTENT, "Session deleted successfully", None
        )


class CreateStudentView(generics.CreateAPIView):
    """Create a new student/instructor in the system."""

    serializer_class = StudentSerializer

    def create(self, request, *args, **kwargs):
        user = request.data.get("user")
        session = request.data.get("session")
        batch_id = request.data.get("batch")

        try:
            batch = Batch.objects.get(batch=batch_id)
        except Batch.DoesNotExist:
            return Response(
                {"error": "Batch does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )

        if Student.objects.filter(user=user, batch=batch).exists():
            return Response(
                {"error": "This user is already registered for this batch."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student_instructor = serializer.save()
            return Response(
                {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Student successfully created",
                    "response": serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentInstructorDetailView(generics.RetrieveAPIView):
    """Retrieve a student/instructor by registration_id."""

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = "registration_id"
