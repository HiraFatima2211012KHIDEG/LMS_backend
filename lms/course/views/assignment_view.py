from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import Assignment,AssignmentSubmission,Grading
from ..serializers import AssignmentSerializer,AssignmentSubmissionSerializer,GradingSerializer

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
        data = request.data
        data['created_by'] = request.user.id 
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Assignment created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating assignment',
            'response': serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)

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
        data = request.data
        data['created_by'] = request.user.id 
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = AssignmentSerializer(assignment, data=data)
        if serializer.is_valid():
            print("jbcuece")
            serializer.save()
            
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Assignment updated successfully',
                'response': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating assignment',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Assignment deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)


class AssignmentSubmissionCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, format=None):
        assignments = AssignmentSubmission.objects.all()
        serializer = AssignmentSubmissionSerializer(assignments, many=True)
        # print(serializer.data)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Assignment submission retrieved successfully',
            'response': serializer.data
        },status=status.HTTP_200_OK)


    def post(self, request, format=None):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = AssignmentSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Assignment submission created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating assignment submission',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

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
        data = request.data.copy()
        data['user'] = request.user.id
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = AssignmentSubmissionSerializer(submission, data=data)
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
        }, status=status.HTTP_204_NO_CONTENT)



class AssignmentGradingListCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        grading = Grading.objects.all()
        serializer = GradingSerializer(grading, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Assignment gradings retrieved successfully',
            'response': serializer.data
        })


    def post(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        serializer = GradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Grading created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating grading',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class AssignmentGradingDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        grading = get_object_or_404(Grading, pk=pk)
        serializer = GradingSerializer(grading)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Assignment grading retrieved successfully',
            'response': serializer.data
        })


    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        grading = get_object_or_404(Grading, pk=pk)
        serializer = GradingSerializer(grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Assignment grading updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating assignment grading',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        grading = get_object_or_404(Grading, pk=pk)
        grading.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Project grading deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)