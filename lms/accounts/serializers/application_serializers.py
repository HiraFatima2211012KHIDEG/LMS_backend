from ..models.user_models import *
from rest_framework import serializers

class TechSkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = TechSkill
        fields = ['id', 'name']


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for the Applications object."""

    class Meta:
        model = Applications
        fields = '__all__'
        extra_kwargs = {
            'program': {'required': False},
            'required_skills': {'required': False},
            'years_of_experience': {'required': False},
            'resume': {'required': False},
        }

    def validate(self, attrs):
        """Custom validation to check fields based on group_name."""
        group_name = attrs.get('group_name')

        if group_name == 'instructor':
            if not attrs.get('years_of_experience'):
                raise serializers.ValidationError({"years_of_experience": "This field is required for instructors."})
            if not attrs.get('required_skills'):
                raise serializers.ValidationError({"required_skills": "This field is required for instructors."})

            if attrs.get('program'):
                raise serializers.ValidationError({"program": "This field should be empty for instructors."})

        elif group_name == 'student':
            if not attrs.get('program'):
                raise serializers.ValidationError({"program": "This field is required for students."})

            # Ensure instructor-specific fields are empty for students
            if attrs.get('years_of_experience') or attrs.get('required_skills') or attrs.get('resume'):
                raise serializers.ValidationError(
                    {"instructor_fields": "years_of_experience, required_skills, and resume should be empty for students."}
                )
        return attrs

    def create(self, validated_data):
        """Create and return an application."""
        programs_data = validated_data.pop('program', None)
        required_skills_data = validated_data.pop('required_skills', None)
        application = Applications.objects.create(**validated_data)

        if programs_data:
            application.program.set(programs_data)
        if required_skills_data:
            application.required_skills.set(required_skills_data)

        return application