from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from accounts.models.user_models import *
import logging
from django.utils import timezone
from decimal import Decimal
from utils.custom import CustomResponseMixin, custom_extend_schema

logger = logging.getLogger(__name__)


class ExamListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        exams = Exam.objects.all()
        serializer = ExamSerializer(exams, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Exams retrieved successfully', serializer.data)

    @custom_extend_schema(ExamSerializer)
    def post(self, request, format=None):
        # data = request.data.copy()
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id


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

    @custom_extend_schema(ExamSerializer)
    def put(self, request, pk, format=None):
        # data = request.data.copy()
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id


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

    # def post(self, request, format=None):
    #     data = {key: value for key, value in request.data.items()}
    #     data['user'] = request.user.id
    #     try:
    #         student_instructor = Student.objects.get(user=request.user)
    #         data['registration_id'] = student_instructor.registration_id
    #     except Student.DoesNotExist:
    #         logger.error("StudentInstructor not found for user: %s", request.user)
    #         return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})
    #     data['status'] = 1
    #     serializer = ExamSubmissionSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return self.custom_response(status.HTTP_201_CREATED, 'Exam submission created successfully', serializer.data)
    #     return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating exam submission', serializer.errors)

    @custom_extend_schema(ExamSubmissionSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['user'] = request.user.id

        try:
            student_instructor = Student.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except Student.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        exam_id = data.get('exam')
        if not exam_id:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Exam ID is required', {})

        # Check if the student has already submitted this exam
        existing_submission = ExamSubmission.objects.filter(
            user=request.user,
            exam_id=exam_id
        ).first()

        if existing_submission:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'You have already submitted this exam', {})

        data['status'] = 1
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

    @custom_extend_schema(ExamSubmissionSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['user'] = request.user.id
        try:
            student_instructor = Student.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except Student.DoesNotExist:
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

    @custom_extend_schema(ExamGradingSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['graded_by'] = request.user.id


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

    @custom_extend_schema(ExamGradingSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['graded_by'] = request.user.id


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
        user = request.user
        exams = Exam.objects.filter(course_id=course_id)

        if not exams.exists():
            return self.custom_response(status.HTTP_200_OK, 'No exams found', {})

        exams_data = []
        for exam in exams:
            submission = ExamSubmission.objects.filter(exam=exam, user=user).first()

            # Determine submission status
            if submission:
                if submission.status == 1:  # Submitted
                    submission_status = 'Submitted'
                else:
                    submission_status = 'Pending'  # Status is pending if not yet graded
            else:
                if timezone.now() > exam.due_date:
                    submission_status = 'Not Submitted'  # Due date has passed without submission
                else:
                    submission_status = 'Pending'  # Due date has not passed, and not yet submitted

            exam_data = {
                'id': exam.id,
                'question': exam.title,
                'description': exam.description,
                'status':exam.status,
                'due_date': exam.due_date,
                'created_at': exam.created_at,
                'submission_status': submission_status,
                'submitted_at': submission.exam_submitted_at if submission else None,
                'submitted_file': submission.exam_submitted_file.url if submission and submission.exam_submitted_file else None,
                'resubmission': submission.resubmission if submission else False,
            }
            exams_data.append(exam_data)

        return self.custom_response(status.HTTP_200_OK, 'Exams retrieved successfully', exams_data)


class ExamStudentListView(CustomResponseMixin, APIView):
    def get(self, request, exam_id,course_id, *args, **kwargs):
        try:
            exam = Exam.objects.get(id=exam_id, course__id=course_id)
        except Exam.DoesNotExist:
            return Response({"detail": "Exam not found for the course."}, status=status.HTTP_404_NOT_FOUND)
        # Retrieve the session associated with the course
        # try:
        #     session = Sessions.objects.get(course__id=course_id)
        # except Sessions.DoesNotExist:
        #     return Response(
        #         {"detail": "Session not found for the course."}, 
        #         status=status.HTTP_404_NOT_FOUND
        #     )
        sessions = Sessions.objects.filter(course__id=course_id)
   
   
        session = sessions.first()
        # Filter students who are enrolled in this session
        enrolled_students = Student.objects.filter(
            studentsession__session=session
        )

        student_list = []
        total_grade = None  # To track the total grade
        for student in enrolled_students:
            user = student.user
            try:
                submission = ExamSubmission.objects.get(exam=exam, user=user)
            except ExamSubmission.DoesNotExist:
                submission = None

            if submission:
                if submission.status == 1:  
                    submission_status = "Submitted"
                else:
                    submission_status = "Pending"  
            else:
                if timezone.now() > exam.due_date:
                    submission_status = "Not Submitted" 
                else:
                    submission_status = "Pending"  

            student_data = {
                'student_name': f"{user.first_name} {user.last_name}",
                'registration_id': student.registration_id,
                'submission_id': submission.id if submission else None,
                'submitted_file': submission.exam_submitted_file.url if submission and submission.exam_submitted_file else None,
                'submitted_at': submission.exam_submitted_at if submission else None,
                'status': submission_status,
                'grade': None,
                'remarks': None
            }

            if submission:
                grading = ExamGrading.objects.filter(exam_submission=submission).first()
                if grading:
                    student_data['grade'] = grading.grade
                    student_data['remarks'] = grading.feedback
                    total_grade = grading.total_grade  
                else:
                    student_data['grade'] = None
                    student_data['remarks'] = None

            student_list.append(student_data)

        response_data = {
            'due_date': exam.due_date,
            'total_grade': total_grade,
            'students': student_list
        }

        return self.custom_response(
            status.HTTP_200_OK, "Students retrieved successfully", response_data
        )




class ExamDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, registration_id):
        exams = Exam.objects.filter(course_id=course_id)
        submissions = ExamSubmission.objects.filter(exam__in=exams, registration_id=registration_id)
        grading_ids = ExamGrading.objects.filter(exam_submission__in=submissions).values_list('exam_submission_id', flat=True)

        exams_data = []
        total_marks_obtained = Decimal('0.0')
        sum_of_total_marks = Decimal('0.0')

        for exam in exams:
            submission = submissions.filter(exam=exam).first()
            grading = ExamGrading.objects.filter(exam_submission=submission).first() if submission else None

            if submission:
                submission_status = 'Submitted' if submission.status == 1 else 'Pending'
            else:
                submission_status = 'Not Submitted' if timezone.now() > exam.due_date else 'Pending'

            marks_obtain = grading.grade if grading else Decimal('0.0')
            total_marks = grading.total_grade if grading else Decimal('0.0')
            remarks = grading.feedback if grading else None

            total_marks_obtained += marks_obtain
            sum_of_total_marks += total_marks

            exam_data = {
                'exam_name': exam.title,
                'marks_obtain': float(marks_obtain),
                'total_marks': float(total_marks),
                'remarks': remarks,
                'status': submission_status,
            }
            exams_data.append(exam_data)

        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Exams retrieved successfully.',
            'data': exams_data,
            'total_marks_obtained': float(total_marks_obtained),
            'sum_of_total_marks': float(sum_of_total_marks)
        })
