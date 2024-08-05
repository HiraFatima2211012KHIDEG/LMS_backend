from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import Assignment,AssignmentSubmission,Grading
from ..serializers import AssignmentSerializer,AssignmentSubmissionSerializer,GradingSerializer
from accounts.models.models_ import *
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


class AssignmentListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        assignments = Assignment.objects.all()
        serializer = AssignmentSerializer(assignments, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Assignment retrieved successfully', serializer.data)


    def post(self, request, format=None):
        data = request.data

        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', serializer.data)


        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Assignment created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating assignment', serializer.errors)

class AssignmentDetailAPIView(CustomResponseMixin,APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = AssignmentSerializer(assignment)
        return self.custom_response(status.HTTP_200_OK, 'Assignment retrieved successfully', serializer.data)
    

    def put(self, request, pk, format=None):
        data = request.data
        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', serializer.data)

        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = AssignmentSerializer(assignment, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Assignment updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating assignment', serializer.errors)


    def delete(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Assignment deleted successfully')



class AssignmentSubmissionCreateAPIView(CustomResponseMixin,APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, format=None):
        assignments = AssignmentSubmission.objects.all()
        serializer = AssignmentSubmissionSerializer(assignments, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Assignment submission retrieved successfully', serializer.data)


    def post(self, request, format=None):
        data = request.data.copy()
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', serializer.data)

        serializer = AssignmentSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Assignment submission created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating assignment submission', serializer.errors)
    

class AssignmentSubmissionDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = AssignmentSubmissionSerializer(submission)
        return self.custom_response(status.HTTP_200_OK, 'Assignment submission retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', serializer.data)

        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = AssignmentSubmissionSerializer(submission, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Assignment submission updated successfully', serializer.data)
    
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating assignment submission', serializer.errors)

    def delete(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        submission.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Assignment submission deleted successfully')



class AssignmentGradingListCreateAPIView(CustomResponseMixin,APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        grading = Grading.objects.all()
        serializer = GradingSerializer(grading, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Assignment gradings retrieved successfully', serializer.data)


    def post(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', serializer.data)

        serializer = GradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Grading created successfully', serializer.data)
        
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating grading', serializer.errors)
    

class AssignmentGradingDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        grading = get_object_or_404(Grading, pk=pk)
        serializer = GradingSerializer(grading)
        return self.custom_response(status.HTTP_200_OK, 'Assignment grading retrieved successfully', serializer.data)


    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', serializer.data)

        grading = get_object_or_404(Grading, pk=pk)
        serializer = GradingSerializer(grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return self.custom_response(status.HTTP_200_OK, 'Assignment grading updated successfully', serializer.data)

        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating assignment grading', serializer.errors)

    def delete(self, request, pk, format=None):
        grading = get_object_or_404(Grading, pk=pk)
        grading.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Project grading deleted successfully')
    