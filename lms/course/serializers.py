from rest_framework import serializers
from .models.models import *


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "name", "short_name", "description", "created_by","status"]


class CourseSerializer(serializers.ModelSerializer):
    # program = serializers.PrimaryKeyRelatedField(
    #     queryset=Program.objects.all(), write_only=True
    # )
    # program_detail = ProgramSerializer(source="program", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "program",
            # "program_detail",
            "description",
            "created_by",
            "credit_hours",
            "status",
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
    # course = serializers.PrimaryKeyRelatedField(
    #     queryset=Course.objects.all(), write_only=True
    # )
    # course_detail = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "course",
            # "course_detail",
            "description",
            "created_by",
            "status",
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
        fields = ['id', 'file',"content_id"]

class ContentSerializer(serializers.ModelSerializer):
    # module_details = ModuleSerializer(source="module", read_only=True)
    # module = serializers.PrimaryKeyRelatedField(
    #     queryset=Module.objects.all(), write_only=True
    # )
    files = ContentFileSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = [
            "id",
            "module",
            # "module_details",
            "name",
            "created_at",
            "updated_at",
            "files",
        ]

   

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id','course', 'created_at','created_by', 'question','description','content' ,'due_date', 'status']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'user', 'submitted_file', 'submitted_at','resubmission','comments']


class GradingSerializer(serializers.ModelSerializer):
    # submission = serializers.PrimaryKeyRelatedField(
    #     queryset=AssignmentSubmission.objects.all(), write_only=True
    # )
    # submission_detail = AssignmentSubmissionSerializer(source="submission", read_only=True)
    class Meta:
        model = Grading
        fields = ['id', 'submission', 'grade','total_grade', 'feedback', 'graded_by', 'graded_at']




class QuizzesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quizzes
        fields = ['id','course', 'created_at', 'created_by', 'question','description','content' ,'due_date', 'status']


class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = ['id', 'quiz', 'user', 'quiz_submitted_file', 'quiz_submitted_at','resubmission','comments']


class QuizGradingSerializer(serializers.ModelSerializer):
    # quiz_submissions = serializers.PrimaryKeyRelatedField(
    #     queryset=QuizSubmission.objects.all(), write_only=True
    # )
    # submission_detail = QuizSubmissionSerializer(source="quiz_submissions", read_only=True)

    class Meta:
        model = QuizGrading
        fields = ['id', 'quiz_submissions', 'grade', 'total_grade', 'feedback', 'graded_by', 'graded_at']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id','course', 'created_at', 'created_by', 'title','description','content' ,'due_date', 'status']


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubmission
        fields = ['id', 'project', 'user', 'project_submitted_file', 'project_submitted_file','resubmission','comments']


class ProjectGradingSerializer(serializers.ModelSerializer):
    # project_submissions = serializers.PrimaryKeyRelatedField(
    #     queryset=ProjectSubmission.objects.all(), write_only=True
    # )
    # submission_detail = ProjectSubmissionSerializer(source="project_submissions", read_only=True)

    class Meta:
        model = ProjectGrading
        fields = ['id', 'project_submissions', 'grade', 'total_grade', 'feedback', 'graded_by', 'graded_at']
       