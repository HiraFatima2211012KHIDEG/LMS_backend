from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from accounts.models.models_ import *
from rest_framework.permissions import IsAuthenticated
import logging


logger = logging.getLogger(__name__)

class CustomResponseMixin:
    def custom_response(self, status_code, message, data):
        return Response(
            {
                'status_code': status_code,
                'message': message,
                'data': data
            },
            status=status_code
        )


class ProgramListCreateAPIView(CustomResponseMixin,APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, format=None):
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        logger.info("Retrieved all programs")
        return self.custom_response(status.HTTP_200_OK, 'Programs retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})
        
        serializer = ProgramSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Created a new program")

            return self.custom_response(status.HTTP_201_CREATED, 'Program created successfully', serializer.data)
        
        logger.error("Error creating a new program: %s", serializer.errors)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating program', serializer.errors)

class ProgramDetailAPIView(CustomResponseMixin,APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, pk, format=None):
        program = get_object_or_404(Program, pk=pk)
        serializer = ProgramSerializer(program)
        logger.info(f"Retrieved program with ID: {pk}")
        return self.custom_response(status.HTTP_200_OK, 'Program retrieved successfully', serializer.data)
    
    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})
        
        program = get_object_or_404(Program, pk=pk)
        serializer = ProgramSerializer(program, data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated program with ID: {pk}")
            return self.custom_response(status.HTTP_200_OK, 'Program updated successfully', serializer.data)
        
        logger.error(f"Error updating program with ID {pk}: {serializer.errors}")
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating program', serializer.errors)
    
    def delete(self, request, pk, format=None):
        program = get_object_or_404(Program, pk=pk)
        program.delete()
        logger.info(f"Deleted program with ID: {pk}")
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Program deleted successfully', {})

class ProgramCoursesAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, program_id, format=None):
        program = get_object_or_404(Program, id=program_id)
        courses = Course.objects.filter(program=program)
        serializer = CourseSerializer(courses, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Courses retrieved successfully', serializer.data)


class CourseModulesAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        course = get_object_or_404(Course, id=course_id)
        modules = Module.objects.filter(course=course)
        serializer = ModuleSerializer(modules, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Modules retrieved successfully', serializer.data)

class ModuleContentAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, module_id, format=None):
        module = get_object_or_404(Module, id=module_id)
        contents = Content.objects.filter(module=module)
        serializer = ContentSerializer(contents, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Content retrieved successfully', serializer.data)


class CourseListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, format=None):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        logger.info("Retrieved all courses")
        return self.custom_response(status.HTTP_200_OK, 'Courses retrieved successfully', serializer.data)
    
    def post(self, request, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})


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



    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})


        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated course with ID: {pk}")
            return self.custom_response(status.HTTP_200_OK, 'Course updated successfully', serializer.data)
        
        logger.error(f"Error updating course with ID {pk}: {serializer.errors}")
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating course', serializer.errors)

    def delete(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.delete()
        logger.info(f"Deleted course with ID: {pk}")
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Course deleted successfully', {})

class ModuleListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Modules retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})


        serializer = ModuleSerializer(data=data)
        if serializer.is_valid():
            module = serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Module created successfully', serializer.data)
        
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating Module', serializer.errors)


class ModuleDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        module = get_object_or_404(Module, pk=pk)
        serializer = ModuleSerializer(module)
        return self.custom_response(status.HTTP_200_OK, 'Module retrieved successfully', serializer.data)
    

    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})


        module = get_object_or_404(Module, pk=pk)
        serializer = ModuleSerializer(module, data=data)
        if serializer.is_valid():
            module = serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Module updated successfully', serializer.data)
        
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating module', serializer.errors)


    def delete(self, request, pk, format=None):
        module = get_object_or_404(Module, pk=pk)
        module.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Module deleted successfully', {})


class ToggleActiveStatusAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, model_name, pk, format=None):
        model = None
        serializer_class = None
        obj = None


        if model_name == 'programs':
            model = Program
            serializer_class = ProgramSerializer
        elif model_name == 'courses':
            model = Course
            serializer_class = CourseSerializer
        elif model_name == 'modules':
            model = Module
            serializer_class = ModuleSerializer
        elif model_name == 'assignments':
            model = Assignment
            serializer_class = AssignmentSerializer
        elif model_name == 'quizzes':
            model = Quizzes
            serializer_class = QuizzesSerializer
        elif model_name == 'projects':
            model = Project
            serializer_class = ProjectSerializer
        else:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Invalid model name')

       
        obj = get_object_or_404(model, pk=pk)
        current_status = obj.status

      
        if current_status == 0:
            obj.status = 1  
        elif current_status == 1:
            obj.status = 0 
        # elif current_status == 2:
        #     obj.status = 0  # Deactivate

        obj.save()

        serializer = serializer_class(obj)
        return self.custom_response(status.HTTP_200_OK, 'Status toggled successfully',serializer.data)
    

class ToggleActiveDeleteStatusAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, model_name, pk, format=None):
        model = None
        serializer_class = None
        obj = None

        if model_name == 'programs':
            model = Program
            serializer_class = ProgramSerializer
        elif model_name == 'courses':
            model = Course
            serializer_class = CourseSerializer
        elif model_name == 'modules':
            model = Module
            serializer_class = ModuleSerializer
        elif model_name == 'assignments':
            model = Assignment
            serializer_class = AssignmentSerializer
        elif model_name == 'quizzes':
            model = Quizzes
            serializer_class = QuizzesSerializer
        elif model_name == 'projects':
            model = Project
            serializer_class = ProjectSerializer
        else:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Invalid model name')

        obj = get_object_or_404(model, pk=pk)
        current_status = obj.status

        if current_status == 0 or 1:
            obj.status = 2 

        obj.save()

        serializer = serializer_class(obj)
        return self.custom_response(status.HTTP_200_OK, 'Status toggled successfully',serializer.data)