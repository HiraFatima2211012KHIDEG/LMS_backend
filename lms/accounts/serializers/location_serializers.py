from rest_framework import serializers
from ..models.user_models import StudentInstructor
from ..models.location_models import (
    City,
    Batch,
    Location,
    Sessions
)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city', 'shortname']


class BatchSerializer(serializers.ModelSerializer):
    batch = serializers.CharField(read_only=True)
    class Meta:
        model = Batch
        fields = ['batch', 'city', 'year', 'no_of_students', 'start_date', 'end_date']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'shortname', 'capacity', 'city']


class SessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sessions
        fields = ['id', 'location', 'no_of_students', 'batch', 'start_time', 'end_time']
