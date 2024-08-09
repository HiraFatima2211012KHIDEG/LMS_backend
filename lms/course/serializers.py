from rest_framework import serializers
from .models.models import *
from .models.program_model import *



class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "short_description",
            "about",
            "created_at",
            "created_by",
            "registration_id",
            "credit_hours",
            "status",
        ]




class ProgramSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(many=True, queryset=Course.objects.all())

    class Meta:
        model = Program
        fields = ["id", "name", "short_description", "about", "created_by","registration_id","status","courses","picture"]


    def create(self, validated_data):
        courses = validated_data.pop('courses', [])
        program = Program.objects.create(**validated_data)
        program.courses.set(courses)
        return program

    def update(self, instance, validated_data):
        courses = validated_data.pop('courses', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.courses.set(courses)
        return instance


class ContentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentFile
        fields = ['id', 'file','module_id']

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
            "registration_id",
            "status",
            "files"
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
        fields = ['id','course', 'created_at','created_by',"registration_id", 'question','description','content' ,'due_date', 'status']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'user',"registration_id", 'submitted_file', 'submitted_at','status','resubmission','comments']


class GradingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grading
        fields = ['id', 'submission', 'grade','total_grade', 'feedback', 'graded_by',"registration_id", 'graded_at']




class QuizzesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quizzes
        fields = ['id','course', 'created_at', 'created_by',"registration_id", 'question','description','content' ,'due_date', 'status']


class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = ['id', 'quiz', 'user',"registration_id", 'quiz_submitted_file', 'quiz_submitted_at','status','resubmission','comments']


class QuizGradingSerializer(serializers.ModelSerializer):
    # quiz_submissions = serializers.PrimaryKeyRelatedField(
    #     queryset=QuizSubmission.objects.all(), write_only=True
    # )
    # submission_detail = QuizSubmissionSerializer(source="quiz_submissions", read_only=True)

    class Meta:
        model = QuizGrading
        fields = ['id', 'quiz_submissions', 'grade', 'total_grade', 'feedback', 'graded_by', "registration_id",'graded_at']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id','course', 'created_at', 'created_by', "registration_id",'title','description','content' ,'due_date', 'status']


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubmission
        fields = ['id', 'project', 'user',"registration_id", 'project_submitted_file', 'project_submitted_file','status','resubmission','comments']


class ProjectGradingSerializer(serializers.ModelSerializer):
    # project_submissions = serializers.PrimaryKeyRelatedField(
    #     queryset=ProjectSubmission.objects.all(), write_only=True
    # )
    # submission_detail = ProjectSubmissionSerializer(source="project_submissions", read_only=True)

    class Meta:
        model = ProjectGrading
        fields = ['id', 'project_submissions', 'grade', 'total_grade', 'feedback', 'graded_by',"registration_id", 'graded_at']
    

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class ExamSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSubmission
        fields = '__all__'

class ExamGradingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamGrading
        fields = '__all__'


class AssignmentProgressSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    student_id = serializers.CharField()
    course_id = serializers.IntegerField()
    total_assignments = serializers.IntegerField()
    submitted_assignments = serializers.IntegerField()
    progress_percentage = serializers.FloatField()