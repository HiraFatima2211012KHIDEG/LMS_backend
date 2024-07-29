from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import Assignment,AssignmentSubmission
from ..serializers import AssignmentSerializer,AssignmentSubmissionSerializer

class AssignmentListCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        assignments = Assignment.objects.all()
        serializer = AssignmentSerializer(assignments, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Assignments retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Assignment created successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating assignment',
            'response': serializer.errors
        })

class AssignmentDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = AssignmentSerializer(assignment)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Assignment retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = AssignmentSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Assignment updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating assignment',
            'response': serializer.errors
        })

    def delete(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Assignment deleted successfully',
            'response': {}
        })


class AssignmentSubmissionCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        serializer = AssignmentSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Assignment submission created successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating assignment submission',
            'response': serializer.errors
        })

class AssignmentSubmissionDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = AssignmentSubmissionSerializer(submission)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Assignment submission retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = AssignmentSubmissionSerializer(submission, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Assignment submission updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating assignment submission',
            'response': serializer.errors
        })

    def delete(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        submission.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Assignment submission deleted successfully',
            'response': {}
        })