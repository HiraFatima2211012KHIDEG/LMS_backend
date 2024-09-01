from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from accounts.models.user_models import *
from accounts.models.attendance_models import *
import logging
from django.shortcuts import get_list_or_404
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from decimal import Decimal
from utils.custom import CustomResponseMixin, custom_extend_schema


logger = logging.getLogger(__name__)


class AssignmentListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        assignments = Assignment.objects.all()
        serializer = AssignmentSerializer(assignments, many=True)
        return self.custom_response(
            status.HTTP_200_OK, "Assignment retrieved successfully", serializer.data
        )

    @custom_extend_schema(AssignmentSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data["created_by"] = request.user.id

        file_content = request.FILES.get("content", None)
        if file_content is not None:
            data["content"] = file_content
        else:
            data["content"] = None

        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status.HTTP_201_CREATED,
                "Assignment created successfully",
                serializer.data,
            )
        return self.custom_response(
            status.HTTP_400_BAD_REQUEST, "Error creating assignment", serializer.errors
        )


class AssignmentDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = AssignmentSerializer(assignment)
        return self.custom_response(
            status.HTTP_200_OK, "Assignment retrieved successfully", serializer.data
        )

    @custom_extend_schema(AssignmentSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data["created_by"] = request.user.id

        assignment = get_object_or_404(Assignment, pk=pk)
        file_content = request.FILES.get("content", None)
        if file_content is not None:
            data["content"] = file_content
        else:
            data["content"] = None
        serializer = AssignmentSerializer(assignment, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status.HTTP_200_OK, "Assignment updated successfully", serializer.data
            )
        return self.custom_response(
            status.HTTP_400_BAD_REQUEST, "Error updating assignment", serializer.errors
        )

    def delete(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.delete()
        return self.custom_response(
            status.HTTP_204_NO_CONTENT, "Assignment deleted successfully", {}
        )


class AssignmentSubmissionCreateAPIView(CustomResponseMixin, APIView):
    # parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        assignments = AssignmentSubmission.objects.all()
        serializer = AssignmentSubmissionSerializer(assignments, many=True)
        return self.custom_response(
            status.HTTP_200_OK,
            "Assignment submissions retrieved successfully",
            serializer.data,
        )

    @custom_extend_schema(AssignmentSubmissionSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data["user"] = request.user.id

        try:
            student_instructor = Student.objects.get(user=request.user)
            data["registration_id"] = student_instructor.registration_id
        except Student.DoesNotExist:
            logger.error("Student not found for user: %s", request.user)
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Student not found for user", {}
            )

        data["status"] = 1
        serializer = AssignmentSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status.HTTP_201_CREATED,
                "Assignment submission created successfully",
                serializer.data,
            )
        return self.custom_response(
            status.HTTP_400_BAD_REQUEST,
            "Error creating assignment submission",
            serializer.errors,
        )

    # def post(self, request, format=None):
    #     data = {key: value for key, value in request.data.items()}
    #     data['user'] = request.user.id

    #     try:
    #         student_instructor = Student.objects.get(user=request.user)
    #         data['registration_id'] = student_instructor.registration_id
    #     except Student.DoesNotExist:
    #         logger.error("Student not found for user: %s", request.user)
    #         return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Student not found for user', {})

    #     assignment_id = data.get('assignment')
    #     if not assignment_id:
    #         return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Assignment ID is required', {})

    #     # Check if the student has already submitted this assignment
    #     existing_submission = AssignmentSubmission.objects.filter(
    #         user=request.user,
    #         assignment_id=assignment_id
    #     ).first()

    #     if existing_submission:
    #         return self.custom_response(status.HTTP_400_BAD_REQUEST, 'You have already submitted this assignment', {})

    #     data['status'] = 1
    #     print("Data to be saved:", data)
    #     serializer = AssignmentSubmissionSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return self.custom_response(status.HTTP_201_CREATED, 'Assignment submission created successfully', serializer.data)

    #     return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating assignment submission', serializer.errors)


class AssignmentSubmissionDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = AssignmentSubmissionSerializer(submission)
        return self.custom_response(
            status.HTTP_200_OK,
            "Assignment submission retrieved successfully",
            serializer.data,
        )

    @custom_extend_schema(AssignmentSubmissionSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data["user"] = request.user.id

        try:
            student_instructor = Student.objects.get(user=request.user)
            data["registration_id"] = student_instructor.registration_id
        except Student.DoesNotExist:
            logger.error("Student not found for user: %s", request.user)
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Student not found for user", {}
            )

        submission = get_object_or_404(AssignmentSubmission, pk=pk)

        if submission.remaining_resubmissions is None:
            submission.remaining_resubmissions = (
                submission.assignment.no_of_resubmissions_allowed
            )

        if submission.decrement_resubmissions():
            serializer = AssignmentSubmissionSerializer(submission, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.custom_response(
                    status.HTTP_200_OK,
                    "Assignment submission updated successfully",
                    serializer.data,
                )
            else:
                return self.custom_response(
                    status.HTTP_400_BAD_REQUEST,
                    "Error updating assignment submission",
                    serializer.errors,
                )
        else:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "No resubmissions left", {}
            )

    def delete(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        submission.delete()
        return self.custom_response(
            status.HTTP_204_NO_CONTENT, "Assignment submission deleted successfully", {}
        )


class AssignmentGradingListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        grading = Grading.objects.all()
        serializer = GradingSerializer(grading, many=True)
        return self.custom_response(
            status.HTTP_200_OK,
            "Assignment gradings retrieved successfully",
            serializer.data,
        )

    @custom_extend_schema(GradingSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data["graded_by"] = request.user.id

        serializer = GradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status.HTTP_201_CREATED, "Grading created successfully", serializer.data
            )

        return self.custom_response(
            status.HTTP_400_BAD_REQUEST, "Error creating grading", serializer.errors
        )


class AssignmentGradingDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        grading = get_object_or_404(Grading, pk=pk)
        serializer = GradingSerializer(grading)
        return self.custom_response(
            status.HTTP_200_OK,
            "Assignment grading retrieved successfully",
            serializer.data,
        )

    @custom_extend_schema(GradingSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data["graded_by"] = request.user.id

        grading = get_object_or_404(Grading, pk=pk)
        serializer = GradingSerializer(grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return self.custom_response(
                status.HTTP_200_OK,
                "Assignment grading updated successfully",
                serializer.data,
            )

        return self.custom_response(
            status.HTTP_400_BAD_REQUEST,
            "Error updating assignment grading",
            serializer.errors,
        )

    def delete(self, request, pk, format=None):
        grading = get_object_or_404(Grading, pk=pk)
        grading.delete()
        return self.custom_response(
            status.HTTP_204_NO_CONTENT, "Project grading deleted successfully", {}
        )


# class AssignmentsByCourseIDAPIView(CustomResponseMixin, APIView):
#     permission_classes = (permissions.IsAuthenticated,)

#     def get(self, request, course_id, format=None):
#         assignments = Assignment.objects.filter(course_id=course_id)


#         if not assignments.exists():
#             return self.custom_response(status.HTTP_200_OK, 'No quizzes found', {})
#         serializer = AssignmentSerializer(assignments, many=True)
#         return self.custom_response(status.HTTP_200_OK, 'Assignments retrieved successfully', serializer.data)
class AssignmentsByCourseIDAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        user = request.user
        assignments = Assignment.objects.filter(course_id=course_id)

        if not assignments.exists():
            return self.custom_response(status.HTTP_200_OK, "No assignments found", {})

        assignments_data = []
        for assignment in assignments:
            submission = AssignmentSubmission.objects.filter(
                assignment=assignment, user=user
            ).first()

            # Determine submission status
            if submission:
                if submission.status == 1:  # Submitted
                    submission_status = "Submitted"
                else:
                    submission_status = "Pending"  # Status is pending if not yet graded
            else:
                if timezone.now() > assignment.due_date:
                    submission_status = (
                        "Not Submitted"  # Due date has passed without submission
                    )
                else:
                    submission_status = (
                        "Pending"  # Due date has not passed, and not yet submitted
                    )

            assignment_data = {
                "id": assignment.id,
                "question": assignment.question,
                "description": assignment.description,
                "status":assignment.status,
                "due_date": assignment.due_date,
                "created_at": assignment.created_at,
                "submission_status": submission_status,
                "submitted_at": submission.submitted_at if submission else None,
                "submitted_file": (
                    submission.submitted_file.url
                    if submission and submission.submitted_file
                    else None
                ),
                "no_of_resubmissions_allowed":assignment.no_of_resubmissions_allowed,
                "remaining_resubmissions": submission.remaining_resubmissions if submission else 0,
            }
            assignments_data.append(assignment_data)

        return self.custom_response(
            status.HTTP_200_OK, "Assignments retrieved successfully", assignments_data
        )


class StudentsWhoSubmittedAssignmentAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, registration_id, format=None):
        submissions = get_list_or_404(
            AssignmentSubmission, registration_id=registration_id
        )
        serializer = AssignmentSubmissionSerializer(submissions, many=True)
        return self.custom_response(
            status.HTTP_200_OK,
            "Users who submitted the assignment retrieved successfully",
            serializer.data,
        )


class StudentsListSubmittedAssignmentAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, assignment_id, format=None):
        # Fetch submissions for the given assignment_id
        submissions = get_list_or_404(AssignmentSubmission, assignment_id=assignment_id)
        serializer = AssignmentSubmissionSerializer(submissions, many=True)
        return self.custom_response(
            status.HTTP_200_OK,
            "Users who submitted the assignment retrieved successfully",
            serializer.data,
        )


class StudentScoresSummaryAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, registration_id):
        # Fetch weightage values
        weightage = Weightage.objects.get(course_id=course_id)

        # assignments = Assignment.objects.filter(course_id=course_id)
        # assignment_submissions = AssignmentSubmission.objects.filter(
        #     assignment__in=assignments,
        #     registration_id=registration_id
        # )
        # assignments_aggregate = Grading.objects.filter(
        #     submission__in=assignment_submissions
        # ).aggregate(
        #     sum_grade=Sum('grade'),
        #     total_sum_grade=Sum('total_grade')
        # )
        # assignments_sum = assignments_aggregate['sum_grade'] or Decimal('0')
        # assignments_total_grades = assignments_aggregate['total_sum_grade'] or Decimal('0')

        quizzes = Quizzes.objects.filter(course_id=course_id)
        quiz_submissions = QuizSubmission.objects.filter(
            quiz__in=quizzes, registration_id=registration_id
        )

        quizzes_aggregate = QuizGrading.objects.filter(
            quiz_submissions__in=quiz_submissions,
            quiz_submissions__registration_id=registration_id,
        ).aggregate(sum_grade=Sum("grade"), total_sum_grade=Sum("total_grade"))
        quizzes_sum = quizzes_aggregate["sum_grade"] or Decimal("0")
        quizzes_total_grades = quizzes_aggregate["total_sum_grade"] or Decimal("0")

        ##########################

        assignments = Assignment.objects.filter(course_id=course_id)
        assignment_submissions = AssignmentSubmission.objects.filter(
            assignment__in=assignments, registration_id=registration_id
        )

        assignments_aggregate = Grading.objects.filter(
            submission__in=assignment_submissions,
            submission__registration_id=registration_id,
        ).aggregate(sum_grade=Sum("grade"), total_sum_grade=Sum("total_grade"))
        assignments_sum = assignments_aggregate["sum_grade"] or Decimal("0")
        assignments_total_grades = assignments_aggregate["total_sum_grade"] or Decimal(
            "0"
        )

        ###########################
        projects = Project.objects.filter(course_id=course_id)
        project_submissions = ProjectSubmission.objects.filter(
            project__in=projects, registration_id=registration_id
        )

        projects_aggregate = ProjectGrading.objects.filter(
            project_submissions__in=project_submissions,
            project_submissions__registration_id=registration_id,
        ).aggregate(sum_grade=Sum("grade"), total_sum_grade=Sum("total_grade"))
        projects_sum = projects_aggregate["sum_grade"] or Decimal("0")
        projects_total_grades = projects_aggregate["total_sum_grade"] or Decimal("0")

        ###########################
        exams = Exam.objects.filter(course_id=course_id)
        exam_submissions = ExamSubmission.objects.filter(
            exam__in=exams, registration_id=registration_id
        )

        exams_aggregate = ExamGrading.objects.filter(
            exam_submission__in=exam_submissions,
            exam_submission__registration_id=registration_id,
        ).aggregate(sum_grade=Sum("grade"), total_sum_grade=Sum("total_grade"))
        exams_sum = exams_aggregate["sum_grade"] or Decimal("0")
        exams_total_grades = exams_aggregate["total_sum_grade"] or Decimal("0")

        # Weightage calculation
        def calculate_percentage(grade_sum, total_grades_sum, weight):
            if total_grades_sum == Decimal("0"):
                return Decimal("0")
            return (grade_sum / total_grades_sum) * weight

        # Get weightage values (ensure conversion to Decimal)
        quizzes_weightage = (
            Decimal(weightage.quizzes_weightage) if weightage else Decimal("0")
        )
        assignments_weightage = (
            Decimal(weightage.assignments_weightage) if weightage else Decimal("0")
        )
        projects_weightage = (
            Decimal(weightage.projects_weightage) if weightage else Decimal("0")
        )
        exams_weightage = (
            Decimal(weightage.exams_weightage) if weightage else Decimal("0")
        )

        # Calculate weighted percentages
        quizzes_percentage = calculate_percentage(
            quizzes_sum, quizzes_total_grades, quizzes_weightage
        )
        assignments_percentage = calculate_percentage(
            assignments_sum, assignments_total_grades, assignments_weightage
        )
        projects_percentage = calculate_percentage(
            projects_sum, projects_total_grades, projects_weightage
        )
        exams_percentage = calculate_percentage(
            exams_sum, exams_total_grades, exams_weightage
        )

        return Response(
            {
                "assignments": {
                    "grades": assignments_sum,
                    "total_grades": assignments_total_grades,
                    "weightage": assignments_weightage,
                    "percentage": assignments_percentage,
                },
                "quizzes": {
                    "grades": quizzes_sum,
                    "total_grades": quizzes_total_grades,
                    "weightage": quizzes_weightage,
                    "percentage": quizzes_percentage,
                },
                "projects": {
                    "grades": projects_sum,
                    "total_grades": projects_total_grades,
                    "weightage": projects_weightage,
                    "percentage": projects_percentage,
                },
                "exams": {
                    "grades": exams_sum,
                    "total_grades": exams_total_grades,
                    "weightage": exams_weightage,
                    "percentage": exams_percentage,
                },
            },
            status=status.HTTP_200_OK,
        )


class AssignmentProgressAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        user = request.user
        course = get_object_or_404(Course, id=course_id)

        try:
            student_instructor = Student.objects.get(user=user)
            registration_id = student_instructor.registration_id
        except Student.DoesNotExist:
            logger.error("Student not found for user: %s", user)
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Student not found for user", {}
            )

        total_assignments = Assignment.objects.filter(course=course).count()
        submitted_assignments = AssignmentSubmission.objects.filter(
            user=user, assignment__course=course
        ).count()

        if total_assignments == 0:
            progress_percentage = 0
        else:
            progress_percentage = (submitted_assignments / total_assignments) * 100

        progress_data = {
            "user_id": user.id,
            "student_id": registration_id,
            "course_id": course_id,
            "total_assignments": total_assignments,
            "submitted_assignments": submitted_assignments,
            "progress_percentage": progress_percentage,
        }

        serializer = AssignmentProgressSerializer(progress_data)
        return self.custom_response(
            status.HTTP_200_OK,
            "Assignment progress retrieved successfully",
            serializer.data,
        )


class QuizProgressAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        user = request.user
        course = get_object_or_404(Course, id=course_id)

        try:
            student_instructor = Student.objects.get(user=user)
            registration_id = student_instructor.registration_id
        except Student.DoesNotExist:
            logger.error("Student not found for user: %s", user)
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Student not found for user", {}
            )

        total_quiz = Quizzes.objects.filter(course=course).count()
        submitted_quiz = QuizSubmission.objects.filter(
            user=user, quiz__course=course
        ).count()

        if total_quiz == 0:
            progress_percentage = 0
        else:
            progress_percentage = (submitted_quiz / total_quiz) * 100

        progress_data = {
            "user_id": user.id,
            "student_id": registration_id,
            "course_id": course_id,
            "total_quiz": total_quiz,
            "submitted_quiz": submitted_quiz,
            "progress_percentage": progress_percentage,
        }

        serializer = QuizProgressSerializer(progress_data)
        return self.custom_response(
            status.HTTP_200_OK, "Quiz progress retrieved successfully", serializer.data
        )


class CourseProgressAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        user = request.user
        course = get_object_or_404(Course, pk=course_id)

        try:
            student_instructor = Student.objects.get(user=user)
            registration_id = student_instructor.registration_id
        except Student.DoesNotExist:
            logger.error("Student not found for user: %s", user)
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Student not found for user", {}
            )
        total_modules = Module.objects.filter(course=course).count()
        attendance_records = Attendance.objects.filter(
            course=course, student=registration_id, status="Present"
        )
        total_attendance = attendance_records.count()

        if total_modules > 0:
            progress_percentage = (total_attendance / total_modules) * 100
        else:
            progress_percentage = 0

        progress_data = {
            "course_id": course_id,
            "user_id": user.id,
            "student_id": registration_id,
            "total_modules": total_modules,
            "total_attendance": total_attendance,
            "progress_percentage": progress_percentage,
        }

        serializer = CourseProgressSerializer(progress_data)
        return self.custom_response(
            status.HTTP_200_OK,
            "Course progress retrieved successfully",
            serializer.data,
        )


def get_pending_assignments_for_student(program_id, registration_id):
    courses = Course.objects.filter(program__id=program_id)
    all_assignments = Assignment.objects.filter(course__in=courses)
    submitted_assignments = AssignmentSubmission.objects.filter(
        assignment__course__in=courses, registration_id=registration_id
    ).values_list("assignment_id", flat=True)
    pending_assignments = (
        all_assignments.exclude(id__in=submitted_assignments)
        .filter(due_date__gte=timezone.now())
        .order_by("due_date")
    )
    return pending_assignments


def get_pending_quizzes_for_student(program_id, registration_id):
    courses = Course.objects.filter(program__id=program_id)
    all_quizzes = Quizzes.objects.filter(course__in=courses)
    submitted_quizzes = QuizSubmission.objects.filter(
        quiz__course__in=courses, registration_id=registration_id
    ).values_list("quiz_id", flat=True)
    pending_quizzes = (
        all_quizzes.exclude(id__in=submitted_quizzes)
        .filter(due_date__gte=timezone.now())
        .order_by("due_date")
    )
    return pending_quizzes


def get_pending_exams_for_student(program_id, registration_id):
    courses = Course.objects.filter(program__id=program_id)
    all_exams = Exam.objects.filter(course__in=courses)
    submitted_exams = ExamSubmission.objects.filter(
        exam__course__in=courses, registration_id=registration_id
    ).values_list("exam_id", flat=True)
    pending_exams = (
        all_exams.exclude(id__in=submitted_exams)
        .filter(due_date__gte=timezone.now())
        .order_by("due_date")
    )
    return pending_exams


def get_pending_projects_for_student(program_id, registration_id):
    courses = Course.objects.filter(program__id=program_id)
    all_projects = Project.objects.filter(course__in=courses)
    submitted_projects = ProjectSubmission.objects.filter(
        project__course__in=courses, registration_id=registration_id
    ).values_list("project_id", flat=True)
    pending_projects = (
        all_projects.exclude(id__in=submitted_projects)
        .filter(due_date__gte=timezone.now())
        .order_by("due_date")
    )
    return pending_projects


class UnifiedPendingItemsView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, program_id, registration_id):
        # Fetch pending items
        pending_assignments = get_pending_assignments_for_student(
            program_id, registration_id
        )
        pending_quizzes = get_pending_quizzes_for_student(program_id, registration_id)
        pending_exams = get_pending_exams_for_student(program_id, registration_id)
        pending_projects = get_pending_projects_for_student(program_id, registration_id)

        # Serialize the data
        assignment_serializer = AssignmentPendingSerializer(
            pending_assignments, many=True
        )
        quiz_serializer = QuizPendingSerializer(pending_quizzes, many=True)
        exam_serializer = ExamPendingSerializer(pending_exams, many=True)
        project_serializer = ProjectPendingSerializer(pending_projects, many=True)

        # Combine and sort the results
        combined_results = []
        combined_results.extend(assignment_serializer.data)
        combined_results.extend(quiz_serializer.data)
        combined_results.extend(exam_serializer.data)
        combined_results.extend(project_serializer.data)

        # Sort combined results by due_date
        sorted_results = sorted(combined_results, key=lambda x: x.get("due_date"))

        # Return the response
        if not sorted_results:
            return self.custom_response(
                status.HTTP_200_OK,
                "All items have been submitted or there are no pending items.",
                data=[],
            )

        return self.custom_response(
            status.HTTP_200_OK,
            "Pending items retrieved successfully.",
            data={"items": sorted_results},
        )


class AssignmentDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, registration_id):
        assignments = Assignment.objects.filter(course_id=course_id)
        submissions = AssignmentSubmission.objects.filter(
            assignment__in=assignments, registration_id=registration_id
        )
        assignments_data = []
        total_marks_obtained = Decimal("0.0")
        sum_of_total_marks = Decimal("0.0")

        for assignment in assignments:
            submission = submissions.filter(assignment=assignment).first()
            grading = (
                Grading.objects.filter(submission=submission).first()
                if submission
                else None
            )

            if submission:
                submission_status = "Submitted" if submission.status == 1 else "Pending"
            else:
                submission_status = (
                    "Not Submitted"
                    if timezone.now() > assignment.due_date
                    else "Pending"
                )

            marks_obtain = grading.grade if grading else Decimal("0.0")
            total_marks = grading.total_grade if grading else Decimal("0.0")
            remarks = grading.feedback if grading else None

            total_marks_obtained += marks_obtain
            sum_of_total_marks += total_marks

            assignment_data = {
                "assignment_name": assignment.question,
                "marks_obtain": float(marks_obtain),
                "total_marks": float(total_marks),
                "remarks": remarks,
                "status": submission_status,
            }
            assignments_data.append(assignment_data)

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Assignments retrieved successfully.",
                "data": assignments_data,
                "total_marks_obtain": float(total_marks_obtained),
                "sum_of_total_marks": float(sum_of_total_marks),
            }
        )
