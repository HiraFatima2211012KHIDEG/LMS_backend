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

class ExamListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        exams = Exam.objects.all()
        serializer = ExamSerializer(exams, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Exams retrieved successfully', serializer.data)

    def post(self, request, format=None):
        # data = request.data.copy()
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

        serializer = ExamSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Exam created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating exam', serializer.errors)

class ExamDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        exam = get_object_or_404(Exam, pk=pk)
        serializer = ExamSerializer(exam)
        return self.custom_response(status.HTTP_200_OK, 'Exam retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        # data = request.data.copy()
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        exam = get_object_or_404(Exam, pk=pk)
        file_content = request.FILES.get('content', None)
        if file_content is not None:
            data['content'] = file_content
        else:
            data['content'] = None
        serializer = ExamSerializer(exam, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Exam updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating exam', serializer.errors)

    def delete(self, request, pk, format=None):
        exam = get_object_or_404(Exam, pk=pk)
        exam.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Exam deleted successfully', {})
    


class ExamSubmissionListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        submissions = ExamSubmission.objects.all()
        serializer = ExamSubmissionSerializer(submissions, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Exam submissions retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = ExamSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Exam submission created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating exam submission', serializer.errors)

class ExamSubmissionDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        submission = get_object_or_404(ExamSubmission, pk=pk)
        serializer = ExamSubmissionSerializer(submission)
        return self.custom_response(status.HTTP_200_OK, 'Exam submission retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        submission = get_object_or_404(ExamSubmission, pk=pk)
        serializer = ExamSubmissionSerializer(submission, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Exam submission updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating exam submission', serializer.errors)

    def delete(self, request, pk, format=None):
        submission = get_object_or_404(ExamSubmission, pk=pk)
        submission.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Exam submission deleted successfully', {})


class ExamGradingListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        gradings = ExamGrading.objects.all()
        serializer = ExamGradingSerializer(gradings, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Exam gradings retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = ExamGradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Exam grading created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating exam grading', serializer.errors)

class ExamGradingDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        grading = get_object_or_404(ExamGrading, pk=pk)
        serializer = ExamGradingSerializer(grading)
        return self.custom_response(status.HTTP_200_OK, 'Exam grading retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        grading = get_object_or_404(ExamGrading, pk=pk)
        serializer = ExamGradingSerializer(grading, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Exam grading updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating exam grading', serializer.errors)

    def delete(self, request, pk, format=None):
        grading = get_object_or_404(ExamGrading, pk=pk)
        grading.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Exam grading deleted successfully', {})

class ExamsByCourseIDAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        # Fetch assignments for the given course_id
        exams = get_list_or_404(Exam, course_id=course_id)
        serializer = ExamSerializer(exams, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Exams retrieved successfully', serializer.data)



class ExamDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, registration_id):
        exams = Exam.objects.filter(course_id=course_id)
        submissions = ExamSubmission.objects.filter(exam__in=exams, registration_id=registration_id)
        grading_ids = ExamGrading.objects.filter(exam_submission__in=submissions).values_list('exam_submission_id', flat=True)

        exams_data = []
        for exam in exams:
            submission = submissions.filter(exam=exam).first()
            grading = ExamGrading.objects.filter(exam_submission=submission).first() if submission else None

            exam_data = {
                'exam_name': exam.title,
                'marks': grading.grade if grading else None,
                'grade': grading.total_grade if grading else None,
                'status': submission.status if submission else 'Not Submitted',
            }
            exams_data.append(exam_data)

        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Exams retrieved successfully.',
            'data': exams_data
        })