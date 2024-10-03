from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from accounts.models.user_models import *
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
import logging
from django.apps import apps
from drf_spectacular.utils import extend_schema
from utils.custom import CustomResponseMixin, custom_extend_schema

logger = logging.getLogger(__name__)


class CourseModulesAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, session_id, format=None):
        course_exists = Course.objects.filter(id=course_id).exists()
        if not course_exists:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND, "Course not found.",{}
            )

        session_exists = Sessions.objects.filter(id=session_id).exists()
        if not session_exists:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND, "Session not found.",{}
            )

        modules = Module.objects.filter(course_id=course_id, session_id=session_id).exclude(status=2).order_by('-created_at')

        if not modules.exists():
            return self.custom_response(
                status.HTTP_200_OK, "No modules found for this course and session.",{}
            )

        serializer = ModuleSerializer(modules, many=True)

        return self.custom_response(
            status.HTTP_200_OK, 'Modules retrieved successfully', serializer.data
        )

class CourseListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, format=None):
        courses = Course.objects.all().order_by('name')
        serializer = CourseSerializer(courses, many=True)
        logger.info("Retrieved all courses")
        return self.custom_response(status.HTTP_200_OK, 'Courses retrieved successfully', serializer.data)


    @custom_extend_schema(CourseSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id
        data['name'] = data.get('name').title()

        serializer = CourseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Created a new course")
            return self.custom_response(status.HTTP_201_CREATED, 'Course created successfully', serializer.data)

        logger.error("Error creating a new course: %s", serializer.errors)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating course', serializer.errors)

class CourseDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course)
        logger.info(f"Retrieved course with ID: {pk}")
        return self.custom_response(status.HTTP_200_OK, 'Course retrieved successfully', serializer.data)


    @custom_extend_schema(CourseSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id


        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated course with ID: {pk}")
            return self.custom_response(status.HTTP_200_OK, 'Course updated successfully', serializer.data)

        logger.error(f"Error updating course with ID {pk}: {serializer.errors}")
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating course', serializer.errors)

    def patch(self, request, pk, format=None):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND, "Course not found.", {}
            )
        
        status_data = request.data.get('status')
        
        if status_data is None:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Status field is required.", {}
            )
        
        serializer = CourseSerializer(course, data={"status": status_data}, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status.HTTP_200_OK, "Course status updated successfully", serializer.data
            )
        
        return self.custom_response(
            status.HTTP_400_BAD_REQUEST, "Error updating course status", serializer.errors
        )

class ModuleListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request, format=None):
        modules = Module.objects.all().order_by('-created_at')
        serializer = ModuleSerializer(modules, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Modules retrieved successfully', serializer.data)


    @custom_extend_schema(ModuleSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id

        # Validate the number of files
        files = request.FILES.getlist('files')
        if len(files) > 5:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'You can upload a maximum of 5 files per module.', {})

        serializer = ModuleSerializer(data=data)
        if serializer.is_valid():
            module = serializer.save()
            for file in files:
                ContentFile.objects.create(module=module, file=file)
            return self.custom_response(status.HTTP_201_CREATED, 'Module created successfully', serializer.data)

        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating Module', serializer.errors)


class ModuleDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser,JSONParser)
    def get(self, request, pk, format=None):
        module = get_object_or_404(Module, pk=pk)
        serializer = ModuleSerializer(module)
        return self.custom_response(status.HTTP_200_OK, 'Module retrieved successfully', serializer.data)

    @custom_extend_schema(ModuleSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id

        module = get_object_or_404(Module, pk=pk)
        serializer = ModuleSerializer(module, data=data)
        if serializer.is_valid():
            module = serializer.save()

            # Validate the number of files
            files = request.FILES.getlist('files')
            if len(files) > 5:
                return self.custom_response(status.HTTP_400_BAD_REQUEST, 'You can upload a maximum of 5 files per module.', {})

            # Handle file updates
            existing_files = set(module.files.values_list('id', flat=True))
            uploaded_files = set()

            # Create new files
            for file in files:
                content_file = ContentFile.objects.create(module=module, file=file)
                uploaded_files.add(content_file.id)

            # Delete old files that are not in the uploaded files
            files_to_delete = existing_files - uploaded_files
            ContentFile.objects.filter(id__in=files_to_delete).delete()
            return self.custom_response(status.HTTP_200_OK, 'Module updated successfully', serializer.data)

        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating module', serializer.errors)


    def patch(self, request, pk, format=None):
        try:
            module = Module.objects.get(pk=pk)
        except Module.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND, "Module not found.",{}
            )
        
        status_data = request.data.get('status')
        
        # Check if status is provided
        if status_data is None:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Status field is required.",{}
            )
        
        serializer = ModuleSerializer(module, data={"status": status_data}, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status.HTTP_200_OK, "Module status updated successfully", serializer.data
            )
        
        return self.custom_response(
            status.HTTP_400_BAD_REQUEST, "Error updating module status", errors=serializer.errors
        )

class ToggleActiveStatusAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    MODEL_SERIALIZER_MAPPING = {
        'programs': ('Program', ProgramSerializer),
        'courses': ('Course', CourseSerializer),
        'modules': ('Module', ModuleSerializer),
        'assignments': ('Assignment', AssignmentSerializer),
        'quizzes': ('Quizzes', QuizzesSerializer),
        'projects': ('Project', ProjectSerializer),
        'exam': ('Exam', ExamSerializer),
        'submissions': ('AssignmentSubmission', AssignmentSubmissionSerializer),
        'quiz_submissions': ('QuizSubmission', QuizSubmissionSerializer),
        'project_submissions': ('ProjectSubmission', ProjectSubmissionSerializer),
        'exam_submissions': ('ExamSubmission', ExamSubmissionSerializer),
    }

    def patch(self, request, model_name, pk, format=None):
        if model_name not in self.MODEL_SERIALIZER_MAPPING:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Invalid model name')

        model_name, serializer_class = self.MODEL_SERIALIZER_MAPPING[model_name]
        model = apps.get_model('course', model_name)

        obj = get_object_or_404(model, pk=pk)
        current_status = obj.status

        obj.status = 1 if current_status == 0 else 0
        obj.save()

        serializer = serializer_class(obj)
        return self.custom_response(status.HTTP_200_OK, 'Status toggled successfully', serializer.data)


class ToggleActiveDeleteStatusAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)
    MODEL_SERIALIZER_MAPPING = {
        'programs': ('Program', ProgramSerializer),
        'courses': ('Course', CourseSerializer),
        'modules': ('Module', ModuleSerializer),
        'assignments': ('Assignment', AssignmentSerializer),
        'quizzes': ('Quizzes', QuizzesSerializer),
        'projects': ('Project', ProjectSerializer),
        'exam': ('Exam', ExamSerializer),
        'submissions': ('AssignmentSubmission', AssignmentSubmissionSerializer),
        'quiz_submissions': ('QuizSubmission', QuizSubmissionSerializer),
        'project_submissions': ('ProjectSubmission', ProjectSubmissionSerializer),
        'exam_submissions': ('ExamSubmission', ExamSubmissionSerializer),
    }

    def patch(self, request, model_name, pk, format=None):
        if model_name not in self.MODEL_SERIALIZER_MAPPING:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Invalid model name')

        model_name, serializer_class = self.MODEL_SERIALIZER_MAPPING[model_name]
        model = apps.get_model('course', model_name)
        obj = get_object_or_404(model, pk=pk)
        current_status = obj.status

        if current_status == 0 or 1:
            obj.status = 2
        obj.save()

        serializer = serializer_class(obj)
        return self.custom_response(status.HTTP_200_OK, 'Status toggled successfully',serializer.data)