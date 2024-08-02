from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import Program, Course, Module,Assignment
from ..serializers import ProgramSerializer, CourseSerializer, ModuleSerializer,ContentFile, AssignmentSerializer
from rest_framework.permissions import IsAuthenticated
import logging


logger = logging.getLogger(__name__)




class ProgramListCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, format=None):
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        logger.info("Retrieved all programs")
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Programs retrieved successfully',
            'response': serializer.data
        })


    def post(self, request, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id 

        serializer = ProgramSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Created a new program")
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Program created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        logger.error("Error creating a new program: %s", serializer.errors)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating program',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProgramDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, pk, format=None):
        program = get_object_or_404(Program, pk=pk)
        serializer = ProgramSerializer(program)
        logger.info(f"Retrieved program with ID: {pk}")
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Program retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id 
        program = get_object_or_404(Program, pk=pk)
        serializer = ProgramSerializer(program, data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated program with ID: {pk}")
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Program updated successfully',
                'response': serializer.data
            })
        logger.error(f"Error updating program with ID {pk}: {serializer.errors}")
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating program',
            'response': serializer.errors
        })

    def delete(self, request, pk, format=None):
        program = get_object_or_404(Program, pk=pk)
        program.delete()
        logger.info(f"Deleted program with ID: {pk}")
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Program deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)

class CourseListCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, format=None):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        logger.info("Retrieved all courses")
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Courses retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id 
        serializer = CourseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Created a new course")
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Course created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        logger.error("Error creating a new course: %s", serializer.errors)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating course',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CourseDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course)
        logger.info(f"Retrieved course with ID: {pk}")
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Course retrieved successfully',
            'response': serializer.data
        })



    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id 
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated course with ID: {pk}")
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Course updated successfully',
                'response': serializer.data
            })
        logger.error(f"Error updating course with ID {pk}: {serializer.errors}")
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating course',
            'response': serializer.errors
        })

    def delete(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.delete()
        logger.info(f"Deleted course with ID: {pk}")
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Course deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)

class ModuleListCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Modules retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id
        serializer = ModuleSerializer(data=data)
        if serializer.is_valid():
            module = serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Module created successfully',
                'response': ModuleSerializer(module).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating module',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ModuleDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        module = get_object_or_404(Module, pk=pk)
        serializer = ModuleSerializer(module)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Module retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['created_by'] = request.user.id
        module = get_object_or_404(Module, pk=pk)
        serializer = ModuleSerializer(module, data=data)
        if serializer.is_valid():
            module = serializer.save()
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Module updated successfully',
                'response': ModuleSerializer(module).data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating module',
            'response': serializer.errors
        })

    def delete(self, request, pk, format=None):
        module = get_object_or_404(Module, pk=pk)
        module.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Module deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)

class ToggleActiveStatusAPIView(APIView):
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
        else:
            return Response({
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid model name',
                'response': {}
            },status=status.HTTP_400_BAD_REQUEST)

        obj = get_object_or_404(model, pk=pk)
        obj.is_active = not obj.is_active
        obj.save()

        serializer = serializer_class(obj)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Status toggled successfully',
            'response': serializer.data
        })