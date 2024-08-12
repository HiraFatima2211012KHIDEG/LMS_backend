from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import AssignmentSerializer,AssignmentSubmissionSerializer,GradingSerializer,AssignmentProgressSerializer
from accounts.models.user_models import *
from accounts.models.attendance_models import *
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


class AssignmentListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        assignments = Assignment.objects.all()
        serializer = AssignmentSerializer(assignments, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Assignment retrieved successfully', serializer.data)


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

        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Assignment created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating assignment', serializer.errors)

class AssignmentDetailAPIView(CustomResponseMixin,APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = AssignmentSerializer(assignment)
        return self.custom_response(status.HTTP_200_OK, 'Assignment retrieved successfully', serializer.data)
    

    def put(self, request, pk, format=None):
        data = {key: value for key, value in request.data.items()}
        data['created_by'] = request.user.id 
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        assignment = get_object_or_404(Assignment, pk=pk)
        file_content = request.FILES.get('content', None)
        if file_content is not None:
            data['content'] = file_content
        else:
            data['content'] = None
        serializer = AssignmentSerializer(assignment, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Assignment updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating assignment', serializer.errors)


    def delete(self, request, pk, format=None):
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Assignment deleted successfully', {})

class AssignmentSubmissionCreateAPIView(CustomResponseMixin, APIView):
    # parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        assignments = AssignmentSubmission.objects.all()
        serializer = AssignmentSubmissionSerializer(assignments, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Assignment submissions retrieved successfully', serializer.data)

    def post(self, request, format=None):
        data = request.data
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = AssignmentSubmissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Assignment submission created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating assignment submission', serializer.errors)
    
class AssignmentSubmissionDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = AssignmentSubmissionSerializer(submission)
        return self.custom_response(status.HTTP_200_OK, 'Assignment submission retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        data = request.data
        data['user'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        serializer = AssignmentSubmissionSerializer(submission, data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Assignment submission updated successfully', serializer.data)
    
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating assignment submission', serializer.errors)

    def delete(self, request, pk, format=None):
        submission = get_object_or_404(AssignmentSubmission, pk=pk)
        submission.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Assignment submission deleted successfully', {})



class AssignmentGradingListCreateAPIView(CustomResponseMixin,APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        grading = Grading.objects.all()
        serializer = GradingSerializer(grading, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Assignment gradings retrieved successfully', serializer.data)


    def post(self, request, pk, format=None):
        data = request.data.copy()
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        serializer = GradingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Grading created successfully', serializer.data)
        
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating grading', serializer.errors)
    

class AssignmentGradingDetailAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        grading = get_object_or_404(Grading, pk=pk)
        serializer = GradingSerializer(grading)
        return self.custom_response(status.HTTP_200_OK, 'Assignment grading retrieved successfully', serializer.data)


    def put(self, request, pk, format=None):
        data = request.data
        data['graded_by'] = request.user.id
        try:
            student_instructor = StudentInstructor.objects.get(user=request.user)
            data['registration_id'] = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", request.user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})

        grading = get_object_or_404(Grading, pk=pk)
        serializer = GradingSerializer(grading, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return self.custom_response(status.HTTP_200_OK, 'Assignment grading updated successfully', serializer.data)

        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating assignment grading', serializer.errors)

    def delete(self, request, pk, format=None):
        grading = get_object_or_404(Grading, pk=pk)
        grading.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Project grading deleted successfully', {})

class AssignmentsByCourseIDAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        # Fetch assignments for the given course_id
        assignments = get_list_or_404(Assignment, course_id=course_id)
        serializer = AssignmentSerializer(assignments, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Assignments retrieved successfully', serializer.data)

class UsersWhoSubmittedAssignmentAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, assignment_id, format=None):
        # Fetch submissions for the given assignment_id
        submissions = get_list_or_404(AssignmentSubmission, assignment_id=assignment_id)
        serializer = AssignmentSubmissionSerializer(submissions, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Users who submitted the assignment retrieved successfully', serializer.data)


class AssignmentProgressAPIView(CustomResponseMixin, APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, format=None):
        user = request.user
        course = get_object_or_404(Course, id=course_id)
  
        try:
            student_instructor = StudentInstructor.objects.get(user=user)
            registration_id = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})
        
        total_assignments = Assignment.objects.filter(course=course).count()
        submitted_assignments = AssignmentSubmission.objects.filter(user=user, assignment__course=course).count()

        if total_assignments == 0:
            progress_percentage = 0
        else:
            progress_percentage = (submitted_assignments / total_assignments) * 100

        progress_data = {
            'user_id': user.id,
            'student_id': registration_id,
            'course_id': course_id,
            'total_assignments': total_assignments,
            'submitted_assignments': submitted_assignments,
            'progress_percentage': progress_percentage
        }

        serializer = AssignmentProgressSerializer(progress_data)
        return self.custom_response(status.HTTP_200_OK, 'Assignment progress retrieved successfully', serializer.data)

class CourseProgressAPIView(CustomResponseMixin,APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id,  format=None):
        user = request.user
        course = get_object_or_404(Course, pk=course_id)
  
        try:
            student_instructor = StudentInstructor.objects.get(user=user)
            registration_id = student_instructor.registration_id
        except StudentInstructor.DoesNotExist:
            logger.error("StudentInstructor not found for user: %s", user)
            return self.custom_response(status.HTTP_400_BAD_REQUEST, 'StudentInstructor not found for user', {})
        total_modules = Module.objects.filter(course=course).count()
        attendance_records = Attendance.objects.filter(session=course, status="Present")
        total_attendance = attendance_records.count()

        
        if total_modules > 0:
            progress_percentage = (total_attendance / total_modules) * 100
        else:
            progress_percentage = 0

        return Response({
            'course_id': course_id,
            'user_id': user.id,
            'student_id': registration_id,
            'total_modules': total_modules,
            'total_attendance': total_attendance,
            'progress_percentage': progress_percentage
        }, status=status.HTTP_200_OK)