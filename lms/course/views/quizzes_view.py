
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from accounts.models.user_models import *
import logging
from django.shortcuts import get_list_or_404


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
class QuizListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        quizzes = Quizzes.objects.all()
        serializer = QuizzesSerializer(quizzes, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Quizzes retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})
        file_content = request.FILES.get('content', None)
        if file_content is not None:
            data['content'] = file_content
        else:
            data['content'] = None
        serializer = QuizzesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Quiz created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating quiz', serializer.errors)


class QuizDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        quiz = get_object_or_404(Quizzes, pk=pk)
        serializer = QuizzesSerializer(quiz)
        return self.custom_response(status.HTTP_200_OK, 'Quiz retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        quiz = get_object_or_404(Quizzes, pk=pk)
        file_content = request.FILES.get('content', None)
        if file_content is not None:
            data['content'] = file_content
        else:
            data['content'] = None
        serializer = QuizzesSerializer(quiz, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Quiz updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating quiz', serializer.errors)

    def delete(self, request, pk, format=None):
        quiz = get_object_or_404(Quizzes, pk=pk)
        quiz.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Quiz deleted successfully', {})

class QuizSubmissionCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        quiz_submissions = QuizSubmission.objects.all()
        serializer = QuizSubmissionSerializer(quiz_submissions, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Quiz submissions retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = request.data
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = QuizSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Quiz submission created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating quiz submission', serializer.errors)


class QuizSubmissionDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        quiz_submission = get_object_or_404(QuizSubmission, pk=pk)
        serializer = QuizSubmissionSerializer(quiz_submission)
        return self.custom_response(status.HTTP_200_OK, 'Quiz submission retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = request.data
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        quiz_submission = get_object_or_404(QuizSubmission, pk=pk)
        serializer = QuizSubmissionSerializer(quiz_submission, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Quiz submission updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating quiz submission', serializer.errors)

    def delete(self, request, pk, format=None):
        quiz_submission = get_object_or_404(QuizSubmission, pk=pk)
        quiz_submission.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Quiz submission deleted successfully', {})


class QuizGradingListCreateAPIVieww(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        quiz_grading = QuizGrading.objects.all()
        serializer = QuizGradingSerializer(quiz_grading, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Quiz gradings retrieved successfully', serializer.data)


    def post(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = QuizGradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Quiz grading created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating quiz grading', serializer.errors)
    
class QuizGradingDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        quiz_grading = get_object_or_404(QuizGrading, pk=pk)
        serializer = QuizGradingSerializer(quiz_grading)
        return self.custom_response(status.HTTP_200_OK, 'Quiz grading retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})
        
        quiz_grading = get_object_or_404(QuizGrading, pk=pk)
        serializer = QuizGradingSerializer(quiz_grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return self.custom_response(status.HTTP_200_OK, 'Quiz grading updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating quiz grading', serializer.errors)

    def delete(self, request, pk, format=None):
        grading = get_object_or_404(QuizGrading, pk=pk)
        grading.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Quiz grading deleted successfully', {})
    
class QuizzesByCourseIDAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        # Fetch assignments for the given course_id
        quizzes = get_list_or_404(Quizzes, course_id=course_id)
        serializer = QuizzesSerializer(quizzes, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Quizzes retrieved successfully', serializer.data)