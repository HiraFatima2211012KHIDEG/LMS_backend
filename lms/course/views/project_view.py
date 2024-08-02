from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
import logging

logger = logging.getLogger(__name__)

class ProjectListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Projects retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        data = request.data
        data['created_by'] = request.user.id 
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Project created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating project',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Project retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        data = request.data
        data['created_by'] = request.user.id
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Project updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating project',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Project deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)




class ProjectSubmissionListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        project_submissions = ProjectSubmission.objects.all()
        serializer = ProjectSubmissionSerializer(project_submissions, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Project submissions retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        data = request.data
        data['user'] = request.user.id
        serializer = ProjectSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Project submission created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating project submission',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ProjectSubmissionDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        project_submission = get_object_or_404(ProjectSubmission, pk=pk)
        serializer = ProjectSubmissionSerializer(project_submission)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Project submission retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        data = request.data
        data['user'] = request.user.id
        project_submission = get_object_or_404(ProjectSubmission, pk=pk)
        serializer = ProjectSubmissionSerializer(project_submission, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Project submission updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating project submission',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project_submission = get_object_or_404(ProjectSubmission, pk=pk)
        project_submission.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Project submission deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)
    



class ProjectGradingListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        project_gradings = ProjectGrading.objects.all()
        serializer = ProjectGradingSerializer(project_gradings, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Project gradings retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        serializer = ProjectGradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Project grading created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating project grading',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ProjectGradingDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        serializer = ProjectGradingSerializer(project_grading)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Project grading retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        serializer = ProjectGradingSerializer(project_grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Project grading updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating project grading',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        project_grading.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Project grading deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)