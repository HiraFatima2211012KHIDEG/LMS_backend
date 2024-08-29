from rest_framework import serializers
from .models.models import *
from .models.program_model import *


class CourseSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all()
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "short_description",
            "about",
            "created_at",
            "created_by",
            "theory_credit_hours",
            "lab_credit_hours",
            "skills",
            "instructors",
            "status",
            "picture",
        ]




class ProgramSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Course.objects.all()
    )

    class Meta:
        model = Program
        fields = [
            "id",
            "name",
            "short_description",
            "about",
            "created_by",
            "status",
            "courses",
            "picture",
        ]

    def create(self, validated_data):
        courses = validated_data.pop("courses", [])
        program = Program.objects.create(**validated_data)
        program.courses.set(courses)
        return program

    def update(self, instance, validated_data):
        courses = validated_data.pop("courses", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.courses.set(courses)
        return instance


class ContentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentFile
        fields = ["id", "file", "module_id"]


class ModuleSerializer(serializers.ModelSerializer):
    files = ContentFileSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "course",
            "description",
            "created_by",
            "status",
            "files",
        ]

    def create(self, validated_data):
        course = validated_data.pop("course")
        return Module.objects.create(course=course, **validated_data)

    def validate(self, data):
        course = data.get("course")
        if not Course.objects.filter(id=course.id).exists():
            raise serializers.ValidationError({"course": "Invalid course ID."})
        return data


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            "id",
            "course",
            "created_at",
            "created_by",
            "question",
            "description",
            "content",
            "due_date",
            "no_of_resubmissions_allowed",
            "status",
        ]


class AssignmentPendingSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(source='course.id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    type = serializers.CharField(default='assignment')
    class Meta:
        model = Assignment
        fields = ['id','type', 'course_id', 'course_name', 'question', 'description', 'created_at', 'due_date', 'status', 'content']

class QuizPendingSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(source='course.id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    type = serializers.CharField(default='quiz')
    class Meta:
        model = Quizzes
        fields = ['id', 'type', 'course_id', 'course_name', 'question', 'description', 'created_at', 'due_date', 'status', 'content']

class ProjectPendingSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(source='course.id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    type = serializers.CharField(default='project')
    class Meta:
        model = Project
        fields = ['id','type',  'course_id', 'course_name', 'title', 'description', 'created_at', 'due_date', 'status', 'content']

class ExamPendingSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(source='course.id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    type = serializers.CharField(default='exam')
    class Meta:
        model = Exam
        fields = ['id','type',  'course_id', 'course_name', 'title', 'description', 'created_at', 'due_date', 'status', 'content']
        
class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = [
            "id",
            "assignment",
            "user",
            "registration_id",
            "submitted_file",
            "submitted_at",
            "status",
            "remaining_resubmissions",
            "comments",
        ]
    def create(self, validated_data):
        assignment_submission = AssignmentSubmission.objects.create(**validated_data)
        return assignment_submission

class GradingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grading
        fields = [
            "id",
            "submission",
            "grade",
            "total_grade",
            "feedback",
            "graded_by",
            "graded_at",
        ]


class QuizzesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quizzes
        fields = [
            "id",
            "course",
            "created_at",
            "created_by",
            "question",
            "description",
            "content",
            "due_date",
            "no_of_resubmissions_allowed",
            "status",
        ]


class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = [
            "id",
            "quiz",
            "user",
            "registration_id",
            "quiz_submitted_file",
            "quiz_submitted_at",
            "status",
            "remaining_resubmissions",
            "comments",
        ]
    def create(self, validated_data):
        quiz_submission = QuizSubmission.objects.create(**validated_data)
        return quiz_submission

class QuizGradingSerializer(serializers.ModelSerializer):
    # quiz_submissions = serializers.PrimaryKeyRelatedField(
    #     queryset=QuizSubmission.objects.all(), write_only=True
    # )
    # submission_detail = QuizSubmissionSerializer(source="quiz_submissions", read_only=True)

    class Meta:
        model = QuizGrading
        fields = [
            "id",
            "quiz_submissions",
            "grade",
            "total_grade",
            "feedback",
            "graded_by",
            "graded_at",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "course",
            "created_at",
            "created_by",
            "title",
            "description",
            "content",
            "due_date",
            "status",
        ]


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubmission
        fields = [
            "id",
            "project",
            "user",
            "registration_id",
            "project_submitted_file",
            "project_submitted_file",
            "status",
            "remaining_resubmissions",
            "comments",
        ]
    def create(self, validated_data):
        project_submission = ProjectSubmission.objects.create(**validated_data)
        return project_submission

class ProjectGradingSerializer(serializers.ModelSerializer):
    # project_submissions = serializers.PrimaryKeyRelatedField(
    #     queryset=ProjectSubmission.objects.all(), write_only=True
    # )
    # submission_detail = ProjectSubmissionSerializer(source="project_submissions", read_only=True)

    class Meta:
        model = ProjectGrading
        fields = [
            "id",
            "project_submissions",
            "grade",
            "total_grade",
            "feedback",
            "graded_by",
            "graded_at",
        ]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = "__all__"


class ExamSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSubmission
        fields = "__all__"


class ExamGradingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamGrading
        fields = "__all__"


class AssignmentProgressSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    student_id = serializers.CharField()
    course_id = serializers.IntegerField()
    total_assignments = serializers.IntegerField()
    submitted_assignments = serializers.IntegerField()
    progress_percentage = serializers.FloatField()


class QuizProgressSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    student_id = serializers.CharField()
    course_id = serializers.IntegerField()
    total_quiz = serializers.IntegerField()
    submitted_quiz = serializers.IntegerField()
    progress_percentage = serializers.FloatField()

class CourseProgressSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    student_id = serializers.CharField()
    course_id = serializers.IntegerField()
    total_modules = serializers.IntegerField()
    total_attendance = serializers.IntegerField()
    progress_percentage = serializers.FloatField()



class WeightageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weightage
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'