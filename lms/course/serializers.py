from rest_framework import serializers
from .models.models import Program, Course, Module

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(read_only=True)
    class Meta:
        model = Course
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    course=CourseSerializer(read_only=True)
    class Meta:
        model = Module
        fields = '__all__'
