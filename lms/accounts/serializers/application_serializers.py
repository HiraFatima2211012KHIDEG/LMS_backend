from ..models.models_ import Applications
from rest_framework import serializers


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = Applications
        fields = '__all__'

    def create(self, validated_data):
        """Create and Return a application"""
        return Applications.objects.create(**validated_data)