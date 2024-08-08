from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.models.user_models import *
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

class ProjectListCreateAPIView(CustomResponseMixin,APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Projects retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = request.data
        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Project created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating project', serializer.errors)

class ProjectDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project)
        return self.custom_response(status.HTTP_200_OK, 'Project retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = request.data
        data['created_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Project updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating project', serializer.errors)

    def delete(self, request, pk, format=None):
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Project deleted successfully', {})




class ProjectSubmissionListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        project_submissions = ProjectSubmission.objects.all()
        serializer = ProjectSubmissionSerializer(project_submissions, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Project submissions retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = request.data
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = ProjectSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.custom_response(status.HTTP_201_CREATED, 'Project submission created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating project submission', serializer.errors)

class ProjectSubmissionDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        project_submission = get_object_or_404(ProjectSubmission, pk=pk)
        serializer = ProjectSubmissionSerializer(project_submission)
        return self.custom_response(status.HTTP_200_OK, 'Project submission retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = request.data
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        project_submission = get_object_or_404(ProjectSubmission, pk=pk)
        serializer = ProjectSubmissionSerializer(project_submission, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.custom_response(status.HTTP_200_OK, 'Project submission updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating project submission', serializer.errors)

    def delete(self, request, pk, format=None):
        project_submission = get_object_or_404(ProjectSubmission, pk=pk)
        project_submission.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Project submission deleted successfully', {})
    



class ProjectGradingListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        project_gradings = ProjectGrading.objects.all()
        serializer = ProjectGradingSerializer(project_gradings, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Project gradings retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = ProjectGradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return self.custom_response(status.HTTP_201_CREATED, 'Project grading created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating project grading', serializer.errors)

class ProjectGradingDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        serializer = ProjectGradingSerializer(project_grading)
        return self.custom_response(status.HTTP_200_OK, 'Project grading retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        serializer = ProjectGradingSerializer(project_grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return self.custom_response(status.HTTP_200_OK, 'Project grading updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating project grading', serializer.errors)


    def delete(self, request, pk, format=None):
        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        project_grading.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Project grading deleted successfully', {})