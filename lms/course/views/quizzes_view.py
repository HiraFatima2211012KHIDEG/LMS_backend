
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from accounts.models.models_ import *
import logging

logger = logging.getLogger(__name__)

class QuizListCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        quizzes = Quizzes.objects.all()
        serializer = QuizzesSerializer(quizzes, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Quizzes retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        data = request.data
        data['created_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return Response({
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'StudentInstructor not found for user',
                'response': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuizzesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Quiz created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating quiz',
            'response': serializer.errors
        })


class QuizDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        quiz = get_object_or_404(Quizzes, pk=pk)
        serializer = QuizzesSerializer(quiz)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Quiz retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        data = request.data
        data['created_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return Response({
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'StudentInstructor not found for user',
                'response': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        quiz = get_object_or_404(Quizzes, pk=pk)
        serializer = QuizzesSerializer(quiz, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Quiz updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating quiz',
            'response': serializer.errors
        })

    def delete(self, request, pk, format=None):
        quiz = get_object_or_404(Quizzes, pk=pk)
        quiz.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Quiz deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)

class QuizSubmissionCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        quiz_submissions = QuizSubmission.objects.all()
        serializer = QuizSubmissionSerializer(quiz_submissions, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Quiz submissions retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        data = request.data
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return Response({
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'StudentInstructor not found for user',
                'response': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuizSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Quiz submission created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating quiz submission',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class QuizSubmissionDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        quiz_submission = get_object_or_404(QuizSubmission, pk=pk)
        serializer = QuizSubmissionSerializer(quiz_submission)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Quiz submission retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        data = request.data
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return Response({
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'StudentInstructor not found for user',
                'response': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        quiz_submission = get_object_or_404(QuizSubmission, pk=pk)
        serializer = QuizSubmissionSerializer(quiz_submission, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Quiz submission updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating quiz submission',
            'response': serializer.errors
        })

    def delete(self, request, pk, format=None):
        quiz_submission = get_object_or_404(QuizSubmission, pk=pk)
        quiz_submission.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Quiz submission deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)


class QuizGradingListCreateAPIVieww(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        quiz_grading = QuizGrading.objects.all()
        serializer = QuizGradingSerializer(quiz_grading, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Quiz gradings retrieved successfully',
            'response': serializer.data
        })


    def post(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return Response({
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'StudentInstructor not found for user',
                'response': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuizGradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Quiz created successfully',
                'response': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating grading',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class QuizGradingDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        quiz_grading = get_object_or_404(QuizGrading, pk=pk)
        serializer = QuizGradingSerializer(quiz_grading)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Quiz grading retrieved successfully',
            'response': serializer.data
        })


    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return Response({
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'StudentInstructor not found for user',
                'response': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        quiz_grading = get_object_or_404(QuizGrading, pk=pk)
        serializer = QuizGradingSerializer(quiz_grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Quiz grading updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating quiz grading',
            'response': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        grading = get_object_or_404(QuizGrading, pk=pk)
        grading.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Quiz grading deleted successfully',
            'response': {}
        }, status=status.HTTP_204_NO_CONTENT)
    
