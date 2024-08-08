from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from ..models.program_model import Program
from accounts.models.user_models import *
from ..serializers import *

import logging
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
logger = logging.getLogger(__name__)

class ProgramListCreateAPIView(CustomResponseMixin, APIView):
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

class ProgramDetailAPIView(CustomResponseMixin, APIView):
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
        courses = program.courses.all()
        serializer = CourseSerializer(courses, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Courses retrieved successfully', serializer.data)