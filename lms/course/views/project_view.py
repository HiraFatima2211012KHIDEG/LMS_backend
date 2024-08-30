from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.models.user_models import *
import logging
from django.utils import timezone
from decimal import Decimal
from utils.custom import CustomResponseMixin, custom_extend_schema

logger = logging.getLogger(__name__)


class ProjectListCreateAPIView(CustomResponseMixin,APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Projects retrieved successfully', serializer.data)

    @custom_extend_schema(ProjectSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id

        file_content = request.FILES.get('content', None)
        if file_content is not None:
            data['content'] = file_content
        else:
            data['content'] = None

        serializer = ProjectSerializer(data=data)
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

    @custom_extend_schema(ProjectSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id


        project = get_object_or_404(Project, pk=pk)
        file_content = request.FILES.get('content', None)
        if file_content is not None:
            data['content'] = file_content
        else:
            data['content'] = None
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

    @custom_extend_schema(ProjectSubmissionSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['user'] = request.user.id
        try:
            student_instructor = Student.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except Student.DoesNotExist:
            logger.error("Student not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Student not found for user', {})
        data['status'] = 1
        serializer = ProjectSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return self.custom_response(status.HTTP_201_CREATED, 'Project submission created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating project submission', serializer.errors)

    # def post(self, request, format=None):
    #     data = {key: value for key, value in request.data.items()}
    #     data['user'] = request.user.id

    #     try:
    #         student_instructor = Student.objects.get(user=request.user)
    #         data['registration_id'] = student_instructor.registration_id
    #     except Student.DoesNotExist:
    #         logger.error("Student not found for user: %s", request.user)
    #         return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Student not found for user', {})

    #     project_id = data.get('project')
    #     if not project_id:
    #         return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Project ID is required', {})

    #     # Check if the student has already submitted this project
    #     existing_submission = ProjectSubmission.objects.filter(
    #         user=request.user,
    #         project_id=project_id
    #     ).first()

    #     if existing_submission:
    #         return self.custom_response(status.HTTP_400_BAD_REQUEST, 'You have already submitted this project', {})

    #     data['status'] = 1
    #     serializer = ProjectSubmissionSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return self.custom_response(status.HTTP_201_CREATED, 'Project submission created successfully', serializer.data)

    #     return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating project submission', serializer.errors)


class ProjectSubmissionDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        project_submission = get_object_or_404(ProjectSubmission, pk=pk)
        serializer = ProjectSubmissionSerializer(project_submission)
        return self.custom_response(status.HTTP_200_OK, 'Project submission retrieved successfully', serializer.data)

    # def put(self, request, pk, format=None):
    #     data = {key: value for key, value in request.data.items()}
    #     data['user'] = request.user.id
    #     try:
    #         student_instructor = Student.objects.get(user=request.user)
    #         data['registration_id'] = student_instructor.registration_id
    #     except Student.DoesNotExist:
    #         logger.error("Student not found for user: %s", request.user)
    #         return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Student not found for user', {})

    #     project_submission = get_object_or_404(ProjectSubmission, pk=pk)
    #     serializer = ProjectSubmissionSerializer(project_submission, data=data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return self.custom_response(status.HTTP_200_OK, 'Project submission updated successfully', serializer.data)
    #     return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating project submission', serializer.errors)

    @custom_extend_schema(ProjectSubmissionSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['user'] = request.user.id
        try:
            student_instructor = Student.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except Student.DoesNotExist:
            logger.error("Student not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Student not found for user', {})

        submission = get_object_or_404(ProjectSubmission, pk=pk)
        if submission.remaining_resubmissions is None:
            submission.remaining_resubmissions = submission.project.no_of_resubmissions_allowed

        if submission.decrement_resubmissions():
            serializer = ProjectSubmissionSerializer(submission, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.custom_response(status.HTTP_200_OK, 'Project submission updated successfully', serializer.data)
            else:
                return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating project submission', serializer.errors)
        else:
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'No resubmissions left', {})



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

    @custom_extend_schema(ProjectGradingSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['graded_by'] = request.user.id


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

    @custom_extend_schema(ProjectGradingSerializer)
    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['graded_by'] = request.user.id


        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        serializer = ProjectGradingSerializer(project_grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return self.custom_response(status.HTTP_200_OK
                                        , 'Project grading updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating project grading', serializer.errors)


    def delete(self, request, pk, format=None):
        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        project_grading.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Project grading deleted successfully', {})



class ProjectsByCourseIDAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        user = request.user
        projects = Project.objects.filter(course_id=course_id)

        if not projects.exists():
            return self.custom_response(status.HTTP_200_OK, 'No projects found', {})

        projects_data = []
        for project in projects:
            submission = ProjectSubmission.objects.filter(project=project, user=user).first()

            # Determine submission status
            if submission:
                if submission.status == 1:  # Submitted
                    submission_status = 'Submitted'
                else:
                    submission_status = 'Pending'  # Status is pending if not yet graded
            else:
                if timezone.now() > project.due_date:
                    submission_status = 'Not Submitted'  # Due date has passed without submission
                else:
                    submission_status = 'Pending'  # Due date has not passed, and not yet submitted

            project_data = {
                'id': project.id,
                'question': project.title,
                'description': project.description,
                'due_date': project.due_date,
                'created_at': project.created_at,
                'submission_status': submission_status,
                'submitted_at': submission.project_submitted_at if submission else None,
                'submitted_file': submission.project_submitted_file.url if submission and submission.project_submitted_file else None,
                'remaining_resubmissions': submission.remaining_resubmissions if submission else False,
                "no_of_resubmissions_allowed":project.no_of_resubmissions_allowed,
                'comments': submission.comments if submission else 0,
            }
            projects_data.append(project_data)

        return self.custom_response(status.HTTP_200_OK, 'Projects retrieved successfully', projects_data)



class ProjectDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, registration_id):
        projects = Project.objects.filter(course_id=course_id)
        submissions = ProjectSubmission.objects.filter(project__in=projects, registration_id=registration_id)
        total_marks_obtained = Decimal('0.0')
        sum_of_total_marks = Decimal('0.0')

        projects_data = []

        for project in projects:
            submission = submissions.filter(project=project).first()
            grading = ProjectGrading.objects.filter(project_submissions=submission).first() if submission else None

            if submission:
                submission_status = 'Submitted' if submission.status == 1 else 'Pending'
            else:
                submission_status = 'Not Submitted' if timezone.now() > project.due_date else 'Pending'

            marks_obtain = grading.grade if grading else Decimal('0.0')
            total_marks = grading.total_grade if grading else Decimal('0.0')
            remarks = grading.feedback if grading else None

            total_marks_obtained += marks_obtain
            sum_of_total_marks += total_marks

            project_data = {
                'project_name': project.title,
                'marks_obtain': float(marks_obtain),
                'total_marks': float(total_marks),
                'remarks': remarks,
                'status': submission_status,
            }
            projects_data.append(project_data)

        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Projects retrieved successfully.',
            'data': projects_data,
            'total_marks_obtained': float(total_marks_obtained),
            'sum_of_total_marks': float(sum_of_total_marks)
        })
