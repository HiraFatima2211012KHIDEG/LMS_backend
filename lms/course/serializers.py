from rest_framework import serializers
from .models.models import Program, Course, Module, Content, ContentFile, Assignment, AssignmentSubmission


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "name", "short_name", "description", "created_by"]


class CourseSerializer(serializers.ModelSerializer):
    program = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), write_only=True
    )
    program_detail = ProgramSerializer(source="program", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "program",
            "program_detail",
            "description",
            "created_by",
            "credit_hours",
            "is_active",
        ]

    def create(self, validated_data):
        program = validated_data.pop("program")
        return Course.objects.create(program=program, **validated_data)

    def validate(self, data):
        program = data.get("program")
        if not Program.objects.filter(id=program.id).exists():
            raise serializers.ValidationError({"program": "Invalid program ID."})
        return data


class ModuleSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True
    )
    course_detail = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "course",
            "course_detail",
            "description",
            "created_by",
            "is_active",
        ]

    def create(self, validated_data):
        course = validated_data.pop("course")
        return Module.objects.create(course=course, **validated_data)

    def validate(self, data):
        course = data.get("course")
        if not Course.objects.filter(id=course.id).exists():
            raise serializers.ValidationError({"course": "Invalid course ID."})
        return data


class ContentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentFile
        fields = ['id', 'file']

class ContentSerializer(serializers.ModelSerializer):
    module_details = ModuleSerializer(source="module", read_only=True)
    module = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all(), write_only=True
    )
    files = ContentFileSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = [
            "id",
            "module",
            "module_details",
            "name",
            "created_at",
            "updated_at",
            "files",
        ]

    # def validate(self, data):
    #     """Ensure that either video_url or lecture_content is provided."""
    #     if not data.get('video_url') and not data.get('lecture_content'):
    #         raise serializers.ValidationError("Either 'video_url' or 'lecture_content' must be provided.")
    #     return data




    # from django.core.exceptions import ValidationError

    # def validate_file_size(file):
    #     """Validate file size (e.g., max size of 10MB)."""
    #     max_size = 10 * 1024 * 1024  # 10 MB
    #     if file.size > max_size:
    #         raise ValidationError(f"File size should not exceed {max_size / (1024 * 1024)} MB.")

    # def validate_file_extension(file):
    #     """Validate file extension."""
    #     allowed_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt']
    #     extension = file.name.split('.')[-1]
    #     if extension not in allowed_extensions:
    #         raise ValidationError(f"Unsupported file extension. Allowed extensions: {', '.join(allowed_extensions)}.")
            
    # def validate_lecture_content(self, value):
    #     validate_file_size(value)
    #     validate_file_extension(value)
    #     return value


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id','module' 'created_at', 'is_active', 'question','description','content', 'due_date']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'user', 'submitted_file', 'submitted_at']