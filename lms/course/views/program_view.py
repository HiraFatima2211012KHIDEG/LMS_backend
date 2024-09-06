from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from ..models.program_model import Program
from ..models.models import Course
from accounts.models.user_models import *
from ..serializers import *
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from utils.custom import CustomResponseMixin, custom_extend_schema

import logging

logger = logging.getLogger(__name__)

class ProgramListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        logger.info("Retrieved all programs")
        return self.custom_response(status.HTTP_200_OK, 'Programs retrieved successfully', serializer.data)

    @custom_extend_schema(ProgramSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id

        serializer = ProgramSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Created a new program")
            return self.custom_response(status.HTTP_201_CREATED, 'Program created successfully', serializer.data)

        logger.error("Error creating a new program: %s", serializer.errors)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating program', serializer.errors)

class ProgramDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        program = get_object_or_404(Program, pk=pk)
        serializer = ProgramSerializer(program)
        logger.info(f"Retrieved program with ID: {pk}")
        return self.custom_response(status.HTTP_200_OK, 'Program retrieved successfully', serializer.data)

    @custom_extend_schema(ProgramSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id


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

    def patch(self, request, pk, format=None):
        program = get_object_or_404(Program, pk=pk)
        course_id = request.data.get('course_id')

        if not course_id:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Course ID is required', {})

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return self.custom_response(status.HTTP_404_NOT_FOUND, 'Course not found', {})

        program.courses.add(course)
        serializer = ProgramSerializer(program)
        logger.info(f"Added course {course_id} to program with ID: {pk}")
        return self.custom_response(status.HTTP_200_OK, 'Course added to program successfully', serializer.data)

class ProgramCoursesAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, program_id, format=None):
        program = get_object_or_404(Program, id=program_id)
        courses = program.courses.all()
        serializer = CourseSerializer(courses, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Courses retrieved successfully', serializer.data)

class ProgramByRegistrationIDAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, registration_id, format=None):
        try:
            # Assuming `Student` model has a foreign key relationship with `Program`
            student = Student.objects.get(registration_id=registration_id)
            program = student.program

            serializer = ProgramSerializer(program)
            logger.info(f"Retrieved program for student with registration ID: {registration_id}")
            return self.custom_response(status.HTTP_200_OK, 'Program retrieved successfully', serializer.data)

        except Student.DoesNotExist:
            logger.error(f"Student with registration ID {registration_id} not found")
            return self.custom_response(status.HTTP_404_NOT_FOUND, 'Student not found', {})

        except Program.DoesNotExist:
            logger.error(f"No program found for student with registration ID {registration_id}")
            return self.custom_response(status.HTTP_404_NOT_FOUND, 'Program not found for the given student', {})


class CreateProgramView(APIView):
    """Create a new Program by providing course IDs and other required details."""

    permission_classes = [permissions.IsAuthenticated]

    # @extend_schema(
    #     request=inline_serializer(
    #         name='ProgramCreateRequest',
    #         fields={
    #             'name': serializers.CharField(max_length=255),
    #             'short_description': serializers.CharField(),
    #             'about': serializers.CharField(),
    #             'courses': serializers.ListField(
    #                 child=serializers.IntegerField(),
    #                 allow_empty=False,
    #                 help_text="List of course IDs to be associated with the program"
    #             ),
    #             'status': serializers.ChoiceField(choices=[(0, 'Inactive'), (1, 'Active')]),
    #             'picture': serializers.ImageField(required=False, allow_null=True)
    #         }
    #     ),
    #     responses={
    #         201: ProgramSerializer,
    #         400: "Bad Request.",
    #         401: "Unauthorized.",
    #     },
    #     description="Create a new Program by providing course IDs and other required details."
    # )
    @custom_extend_schema(ProgramSerializer)
    def post(self, request, *args, **kwargs):
        course_ids = request.data.get('courses')
        if not course_ids:
            return Response({"detail": "Courses list cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            courses = Course.objects.filter(id__in=course_ids)
            if len(courses) != len(course_ids):
                return Response({"detail": "One or more course IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"detail": "Invalid course IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        program_data = {
            'name': request.data.get('name'),
            'short_description': request.data.get('short_description'),
            'about': request.data.get('about'),
            'created_by': request.user.id,
            'courses': [],
            'status': request.data.get('status', 0),
            'picture': request.data.get('picture', None)
        }

        program_serializer = ProgramSerializer(data=program_data)
        if program_serializer.is_valid():
            program = program_serializer.save()
            program.courses.set(courses)
            return Response(ProgramSerializer(program).data, status=status.HTTP_201_CREATED)
        else:
            return Response(program_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
