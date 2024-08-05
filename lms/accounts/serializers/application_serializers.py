from ..models.models_ import Applications
from rest_framework import serializers


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for the Applications object."""

    class Meta:
        model = Applications
        fields = '__all__'

    def create(self, validated_data):
        """Create and return an application."""
        return Applications.objects.create(**validated_data)
