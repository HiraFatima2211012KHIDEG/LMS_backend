from rest_framework import viewsets, mixins, status, generics, permissions
from rest_framework.response import Response
from ..models.location_models import (
    City,
    Batch,
    Location,
    Sessions
)
from ..serializers.location_serializers import (
    CitySerializer,
    BatchSerializer,
    LocationSerializer,
    SessionsSerializer,
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

class BaseLocationViewSet(CustomResponseMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(status.HTTP_201_CREATED, 'created successfully', response.data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.custom_response(status.HTTP_200_OK, 'updated successfully', response.data)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'deleted successfully', None)


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
