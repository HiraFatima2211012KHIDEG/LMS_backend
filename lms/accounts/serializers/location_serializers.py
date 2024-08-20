from rest_framework import serializers
from ..models.models_ import City, Batch, Location, Sessions, Student
# from .location_serializers import SessionsSerializer

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city', 'shortname']


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['city', 'year', 'no_of_students', 'start_date', 'end_date']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'shortname', 'capacity', 'city']


class SessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sessions
        fields = ['location', 'no_of_students', 'batch', 'start_time', 'end_time']


class StudentSerializer(serializers.ModelSerializer):
    registration_id = serializers.CharField(read_only=True)
    # session = SessionsSerializer()
    class Meta:
        model = Student
        fields = ['registration_id','user', 'session']

