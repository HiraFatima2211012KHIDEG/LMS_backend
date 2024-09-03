from rest_framework import serializers

from ..models.user_models import Student
from ..models.location_models import City, Batch, Location, Sessions


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["city", "shortname"]


class BatchSerializer(serializers.ModelSerializer):
    batch = serializers.CharField(read_only=True)

    class Meta:
        model = Batch
        fields = [
            "batch",
            "city",
            "city_abb",
            "year",
            "no_of_students",
            "start_date",
            "end_date",
            "status",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "shortname", "capacity", "city", "status"]


class SessionsSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)

    class Meta:
        model = Sessions

        fields = [
            "location",
            "location_name",
            "no_of_students",
            "batch",
            "start_time",
            "end_time",
            "status",
        ]


class AssignSessionsSerializer(serializers.Serializer):
    session_ids = serializers.ListField(child=serializers.IntegerField())

    def validate_session_ids(self, value):
        if not Sessions.objects.filter(id__in=value).exists():
            raise serializers.ValidationError("Some session IDs are invalid.")
        return value
