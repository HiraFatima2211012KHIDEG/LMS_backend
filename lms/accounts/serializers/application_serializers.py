from ..models.models_ import Applications
from rest_framework import serializers


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for the Applications object."""

    class Meta:
        model = Applications
        fields = '__all__'

    # def validate(self, attrs):
    #     # Extract the program and its start date
    #     program = attrs['program']
    #     start_date = program.start_date

    #     # Check if an application with the same email, program, and start date already exists
    #     if Applications.objects.filter(
    #         email=attrs['email'],
    #         program=program,
    #     ).exists():
    #         raise serializers.ValidationError("You have already applied for this program starting on this date.")
    #     return attrs

    #add validation logic here to check email, program and start_date if already exists.We might need to create a new table here for program and start end id.

    def create(self, validated_data):
        """Create and return an application."""
        return Applications.objects.create(**validated_data)
