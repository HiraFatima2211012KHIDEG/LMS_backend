from rest_framework import viewsets, mixins, status, generics
from rest_framework.response import Response
from ..models.models_ import (
    City,
    Batch,
    Location,
    Sessions,
    StudentInstructor
)
from ..serializers.location_serializers import (
    CitySerializer,
    BatchSerializer,
    LocationSerializer,
    SessionsSerializer,
    StudentInstructorSerializer
    )

class CustomResponseMixin:
    def custom_response(self, status_code, message, data):
        return Response(
            {
                'status_code': status_code,
                'message': message,
                'data': data
            },
            status=status_code
        )

class CityViewSet(CustomResponseMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(status.HTTP_201_CREATED, 'City created successfully', response.data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.custom_response(status.HTTP_200_OK, 'City updated successfully', response.data)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'City deleted successfully', None)

class BatchViewSet(CustomResponseMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(status.HTTP_201_CREATED, 'Batch created successfully', response.data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.custom_response(status.HTTP_200_OK, 'Batch updated successfully', response.data)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Batch deleted successfully', None)

class LocationViewSet(CustomResponseMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(status.HTTP_201_CREATED, 'Location created successfully', response.data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.custom_response(status.HTTP_200_OK, 'Location updated successfully', response.data)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Location deleted successfully', None)

class SessionsViewSet(CustomResponseMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Sessions.objects.all()
    serializer_class = SessionsSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(status.HTTP_201_CREATED, 'Session created successfully', response.data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.custom_response(status.HTTP_200_OK, 'Session updated successfully', response.data)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Session deleted successfully', None)


class CreateStudentInstructorView(generics.CreateAPIView):
    """Create a new student/instructor in the system."""
    serializer_class = StudentInstructorSerializer

    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        session = request.data.get('session')
        batch_id = request.data.get('batch')

        try:
            batch = Batch.objects.get(batch=batch_id)
        except Batch.DoesNotExist:
            return Response({'error': 'Batch does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        if StudentInstructor.objects.filter(user=user, batch=batch).exists():
            return Response({'error': 'This user is already registered for this batch.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student_instructor = serializer.save()
            return Response({'status_code': status.HTTP_201_CREATED,
                  'message': 'StudentInstructor successfully created',
                  'response': serializer.data})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentInstructorDetailView(generics.RetrieveAPIView):
    """Retrieve a student/instructor by registration_id."""
    queryset = StudentInstructor.objects.all()
    serializer_class = StudentInstructorSerializer
    lookup_field = 'registration_id'
