from rest_framework import viewsets, mixins, status, generics, permissions
from rest_framework.response import Response
from ..models.location_models import (
    City,
    Batch,
    Location,
    Sessions,
)
from utils.custom import BaseLocationViewSet
from ..serializers.location_serializers import (
    CitySerializer,
    BatchSerializer,
    LocationSerializer,
    SessionsSerializer,
)
from rest_framework import views
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



class CreateBatchLocationSessionView(views.APIView):

    @extend_schema(
        request=inline_serializer(
            name='BatchLocationSession',
            fields={
                'batch': BatchSerializer(),
                'location': LocationSerializer(),
                'session': SessionsSerializer(),
            }
        ),
        responses={
            200: "Successful.",
            400: "Bad Request.",
            401: "Unauthorized.",
        },
        description="Create or get Batch, Location, and Session in a single API call."
    )
    def post(self, request, *args, **kwargs):
        batch = request.data.get('batch')
        location = request.data.get('location')

        try:
            batch = Batch.objects.get(batch=batch)
        except Batch.DoesNotExist:
            return Response({"detail": "Batch not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = Location.objects.get(id=location)
        except Location.DoesNotExist:
            return Response({"detail": "Location not found."}, status=status.HTTP_400_BAD_REQUEST)

        session_data = request.data.get('session')
        session_data['location'] = location.id
        session_data['batch'] = batch.batch
        session_serializer = SessionsSerializer(data=session_data)
        if session_serializer.is_valid():
            session_serializer.save()
        else:
            return Response(session_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'batch': BatchSerializer(batch).data,
            'location': LocationSerializer(location).data,
            'session': session_serializer.data
        }, status=status.HTTP_201_CREATED)
