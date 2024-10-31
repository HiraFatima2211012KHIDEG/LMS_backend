from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
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
        projects = Project.objects.all().order_by('-created_at')
        serializer = ProjectSerializer(projects, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Projects retrieved successfully', serializer.data)

    @custom_extend_schema(ProjectSerializer)
    def post(self, request, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id

        file_content = request.data.get('content', None)
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
        file_content = request.data.get('content', None)
        if file_content is not None:
            data['content'] = file_content
        else:
            data['content'] = None
        serializer = ProjectSerializer(project, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Project updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating project', serializer.errors)

    def patch(self, request, pk, format=None):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND, "Project not found.", {}
            )
        
        status_data = request.data.get('status')
        
        if status_data is None:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Status field is required.", {}
            )
        
        serializer = ProjectSerializer(project, data={"status": status_data}, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status.HTTP_200_OK, "Project status updated successfully", serializer.data
            )
        
        return self.custom_response(
            status.HTTP_400_BAD_REQUEST, "Error updating project status", errors=serializer.errors
        )



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

        # Check if grading already exists
        if ProjectGrading.objects.filter(project_submissions=data['project_submissions'], graded_by=request.user).exists():
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Project grading already exists for this submission', None)
        
        # Retrieve the project submission associated with the grading
        project_submission = get_object_or_404(ProjectSubmission, pk=data['project_submissions'])
        total_grade = project_submission.project.total_grade  # Get the total grade for the associated project

        # Validate the grade
        if 'grade' in data and float(data['grade']) > float(total_grade):
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                f"Grade cannot exceed the total grade of {total_grade}",
                None
            )

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

        # Retrieve the associated project submission
        project_submission = project_grading.project_submissions
        total_grade = project_submission.project.total_grade  # Get the total grade for the associated project

        # Validate the grade
        if 'grade' in data and float(data['grade']) > float(total_grade):
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                f"Grade cannot exceed the total grade of {total_grade}",
                None
            )

        serializer = ProjectGradingSerializer(project_grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return self.custom_response(status.HTTP_200_OK, 'Project grading updated successfully', serializer.data)

        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating project grading', serializer.errors)


    def delete(self, request, pk, format=None):
        project_grading = get_object_or_404(ProjectGrading, pk=pk)
        project_grading.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Project grading deleted successfully', {})



class ProjectsByCourseIDAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id,session_id, format=None):
        user = request.user
        # projects = Project.objects.filter(course_id=course_id,session_id=session_id).exclude(Q(status=2) | Q(status=0)).order_by('-created_at')
        is_student = Student.objects.filter(user=user).exists()
        
        if is_student:
            projects = Project.objects.filter(course_id=course_id,session_id=session_id).exclude(Q(status=2) | Q(status=0)).order_by('-created_at')
        else:
            projects = Project.objects.filter(course_id=course_id,session_id=session_id).exclude(status=2).order_by('-created_at')
        
        if not projects.exists():
            return self.custom_response(status.HTTP_200_OK, 'No projects found', {})

        projects_data = []
        for project in projects:
            submission = ProjectSubmission.objects.filter(project=project, user=user).first()

            if submission:
                if submission.status == 1:  # Submitted
                    # if submission.project_submitted_at > project.due_date:
                    #     submission_status = "Late Submission"
                    # else:
                    submission_status = "Submitted"
                else:
                    submission_status = "Pending"  # Status is pending if not yet graded
            else:
                if timezone.now() > project.due_date:
                    submission_status = (
                        "Not Submitted"  # Due date has passed without submission
                    )
                else:
                    submission_status = (
                        "Pending"  # Due date has not passed, and not yet submitted
                    )
            session_data = {
                "id": project.session.id,
            } if project.session else None
            project_data = {
                'id': project.id,
                'total_grade':project.total_grade,
                'content': project.content if project.content else None, 
                'question': project.title,
                'description': project.description,
                'late_submission':project.late_submission,
                'session': session_data,
                'status':project.status,
                'due_date': project.due_date,
                'created_at': project.created_at,
                'submission_id':  submission.id if submission else None,
                'submission_status': submission_status,
                'submitted_at': submission.project_submitted_at if submission else None,
                'submitted_file': submission.submitted_file if submission and submission.submitted_file else None,
                'remaining_resubmissions': submission.remaining_resubmissions if submission else False,
                "no_of_resubmissions_allowed":project.no_of_resubmissions_allowed,
                'comments': submission.comments if submission else 0,
            }
            projects_data.append(project_data)

        return self.custom_response(status.HTTP_200_OK, 'Projects retrieved successfully', projects_data)



class ProjectDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id,session_id, registration_id):
        projects = Project.objects.filter(course_id=course_id,session_id=session_id).exclude(Q(status=2) | Q(status=0))
        submissions = ProjectSubmission.objects.filter(project__in=projects, registration_id=registration_id)
        total_marks_obtained = Decimal('0.0')
        sum_of_total_marks = Decimal('0.0')

        projects_data = []

        for project in projects:
            submission = submissions.filter(project=project).first()
            grading = ProjectGrading.objects.filter(project_submissions=submission).first() if submission else None

            if submission:
                if submission.status == 1:  # Submitted
                    # if submission.project_submitted_at > project.due_date:
                    #     submission_status = "Late Submission"
                    # else:
                    submission_status = "Submitted"
                else:
                    submission_status = "Pending"  # Status is pending if not yet graded
            else:
                if timezone.now() > project.due_date:
                    submission_status = (
                        "Not Submitted"  # Due date has passed without submission
                    )
                else:
                    submission_status = (
                        "Pending"  # Due date has not passed, and not yet submitted
                    )

            marks_obtain = grading.grade if grading else Decimal('0.0')
            total_marks = project.total_grade if project.total_grade is not None else Decimal('0.0')
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


# class QuizStudentListView(CustomResponseMixin, APIView):
#     permission_classes = (permissions.IsAuthenticated,)

#     def get(self, request, quiz_id, course_id, *args, **kwargs):
#         try:
#             # Retrieve the quiz based on quiz ID and course ID
#             quiz = Quizzes.objects.get(id=quiz_id, course__id=course_id)
#         except Quizzes.DoesNotExist:
#             return Response(
#                 {"detail": "Quiz not found for the course."}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # Retrieve the session associated with the course
#         sessions = Sessions.objects.filter(course__id=course_id)
#         print(sessions)
   
#         session = sessions.first()
#         print(session)  
#         # Filter students who are enrolled in this session
#         enrolled_students = Student.objects.filter(
#             studentsession__session=session
#         )
#         print(enrolled_students)  
#         student_list = []
#         total_grade = quiz.total_grade 

#         # Process each student's quiz submission
#         for student in enrolled_students:
#             user = student.user
#             try:
#                 submission = QuizSubmission.objects.get(quiz=quiz, user=user)
#             except QuizSubmission.DoesNotExist:
#                 submission = None

#             if submission:
#                 submission_status = "Submitted" if submission.status == 1 else "Pending"
#             else:
#                 submission_status = (
#                     "Not Submitted" if timezone.now() > quiz.due_date else "Pending"
#                 )

#             # Collect student data
#             student_data = {
#                 'quiz':quiz.id,
#                 'student_name': f"{user.first_name} {user.last_name}",
#                 'registration_id': student.registration_id,
#                 'submission_id': submission.id if submission else None,
#                 'submitted_file': submission.quiz_submitted_file.url if submission and submission.quiz_submitted_file else None,
#                 'submitted_at': submission.quiz_submitted_at if submission else None,
#                 'status': submission_status,
#                 'grade': 0,
#                 'remarks': None
#             }

#             if submission:
#                 grading = QuizGrading.objects.filter(quiz_submissions=submission).first()
#                 if grading:
#                     student_data['grade'] = grading.grade
#                     student_data['remarks'] = grading.feedback
                   

#             student_list.append(student_data)

#         response_data = {
#             'due_date': quiz.due_date,
#             'total_grade': total_grade,
#             'students': student_list
#         }

#         return self.custom_response(
#             status.HTTP_200_OK, "Students retrieved successfully", response_data
#         )



# class ProjectStudentListView(CustomResponseMixin, APIView):
#     def get(self, request, project_id,course_id, *args, **kwargs):
#         try:
#             project = Project.objects.get(id=project_id, course__id=course_id)
#         except Project.DoesNotExist:
#             return Response({"detail": "Project not found for the course."}, status=status.HTTP_404_NOT_FOUND)

#         sessions = Sessions.objects.filter(course__id=course_id)
   
   
#         session = sessions.first()        
#         # Filter students who are enrolled in this session
#         enrolled_students = Student.objects.filter(
#             studentsession__session=session
#         )

#         student_list = []
#         total_grade = project.total_grade 

#         for student in enrolled_students:
#             user = student.user
#             try:
#                 submission = ProjectSubmission.objects.get(project=project, user=user)
#             except ProjectSubmission.DoesNotExist:
#                 submission = None

#             if submission:
#                 if submission.status == 1:  
#                     submission_status = "Submitted"
#                 else:
#                     submission_status = "Pending"  
#             else:
#                 if timezone.now() > project.due_date:
#                     submission_status = "Not Submitted"  
#                 else:
#                     submission_status = "Pending"  

#             student_data = {
#                 'project':project.id,
#                 'student_name': f"{user.first_name} {user.last_name}",
#                 'registration_id': student.registration_id,
#                 'submission_id': submission.id if submission else None,
#                 'submitted_file': submission.project_submitted_file.url if submission and submission.project_submitted_file else None,
#                 'submitted_at': submission.project_submitted_at if submission else None,
#                 'status': submission_status,
#                 'grade': 0,
#                 'remarks': None
#             }

#             if submission:
#                 grading = ProjectGrading.objects.filter(project_submissions=submission).first()
#                 if grading:
#                     student_data['grade'] = grading.grade
#                     student_data['remarks'] = grading.feedback
                      
#                 else:
#                     student_data['grade'] = 0
#                     student_data['remarks'] = None

#             student_list.append(student_data)

#         response_data = {
#             'due_date': project.due_date,
#             'total_grade': total_grade,
#             'students': student_list
#         }

#         return self.custom_response(
#             status.HTTP_200_OK, "Students retrieved successfully", response_data
#         )


class ProjectStudentListView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, project_id, course_id, session_id, *args, **kwargs):
        try:
            # Retrieve the project based on project ID and course ID
            project = Project.objects.get(id=project_id, course__id=course_id,session_id=session_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found for the course."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the specific session using the session_id
        try:
            session = Sessions.objects.get(id=session_id, course__id=course_id)
        except Sessions.DoesNotExist:
            return Response(
                {"detail": "Session not found for the course."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Filter students who are enrolled in this session
        enrolled_students = Student.objects.filter(
            studentsession__session=session
        )

        student_list = []
        total_grade = project.total_grade 

        # Process each student's project submission
        for student in enrolled_students:
            user = student.user
            try:
                submission = ProjectSubmission.objects.get(project=project, user=user)
            except ProjectSubmission.DoesNotExist:
                submission = None

            if submission:
                if submission.status == 1:  # Submitted
                    # if submission.project_submitted_at > project.due_date:
                    #     submission_status = "Late Submission"
                    # else:
                    submission_status = "Submitted"
                else:
                    submission_status = "Pending"  # Status is pending if not yet graded
            else:
                if timezone.now() > project.due_date:
                    submission_status = (
                        "Not Submitted"  # Due date has passed without submission
                    )
                else:
                    submission_status = (
                        "Pending"  # Due date has not passed, and not yet submitted
                    )

            # Collect student data
            student_data = {
                'project': project.id,
                'student_name': f"{user.first_name} {user.last_name}",
                'registration_id': student.registration_id,
                'submission_id': submission.id if submission else None,
                'submitted_file': submission.submitted_file if submission and submission.submitted_file else None,
                'submitted_at': submission.project_submitted_at if submission else None,
                'comments':submission.comments if submission else None,
                'status': submission_status,
                'grade': 0,
                'remarks': None,
                'grading_id': None, 
            }

            if submission:
                grading = ProjectGrading.objects.filter(project_submissions=submission).first()
                if grading:
                    student_data['grade'] = grading.grade
                    student_data['remarks'] = grading.feedback
                    student_data['grading_id'] = grading.id 

            student_list.append(student_data)

        # Prepare response data
        response_data = {
            'due_date': project.due_date,
            'total_grade': total_grade,
            'students': student_list
        }

        return self.custom_response(
            status.HTTP_200_OK, "Students retrieved successfully", response_data
        )
