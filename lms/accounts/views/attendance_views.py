from rest_framework import generics, filters, viewsets,permissions
from rest_framework.response import Response
from rest_framework import status
from ..models.attendance_models import Attendance
from ..serializers.attendance_serializers import AttendanceSerializer
from .location_views import BaseLocationViewSet
from django_filters.rest_framework import DjangoFilterBackend
from utils.custom import CustomResponseMixin
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from ..models.location_models import Sessions
from ..models.user_models import StudentSession, Student, InstructorSession, Instructor
from rest_framework.views import APIView
from ..serializers.attendance_serializers import AttendanceSerializer,StudentDetailAttendanceSerializer
from django.utils import timezone
from ..serializers.location_serializers import InstructorSessionSerializer
from ..models.user_models import User
class AttendanceListCreateView(BaseLocationViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "date", "course", "marked_by"]
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "int",
                        "description": "Course id for attendance",
                    },
                },
                "required": ["course_id"],
            }
        },
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        course_id = request.query_params.get("course_id")
        if not course_id:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "course_id query parameter is required.",
                None,
            )
        # Determine if the request is for bulk creation
        if isinstance(request.data, list):
            for item in request.data:
                item["marked_by"] = user.email
                item["course"] = course_id
            # Validate and create multiple instances
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            # Single attendance record creation
            request.data["marked_by"] = user.email
            request.data["course"] = course_id
            serializer = self.get_serializer(data=request.data)
        # Validate the data
        serializer.is_valid(raise_exception=True)
        # Perform the creation
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return self.custom_response(
            status.HTTP_201_CREATED,
            "created successfully",
            serializer.data
        )


# class AttendanceListCreateView(BaseLocationViewSet):
#     queryset = Attendance.objects.all()
#     serializer_class = AttendanceSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ["student", "date", "course", "marked_by"]

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         course_id = request.query_params.get('course_id')

#         if not course_id:
#             return self.custom_response(
#                 status.HTTP_400_BAD_REQUEST,
#                 "course_id query parameter is required.",
#                 None
#             )

#         # Determine if the request is for bulk creation
#         if isinstance(request.data, list):
#             for item in request.data:
#                 item['marked_by'] = user.email
#                 item['course'] = course_id

#             # Validate and create multiple instances
#             serializer = self.get_serializer(data=request.data, many=True)
#         else:
#             # Single attendance record creation
#             request.data['marked_by'] = user.email
#             request.data['course'] = course_id
#             serializer = self.get_serializer(data=request.data)

#         # Validate the data
#         serializer.is_valid(raise_exception=True)

#         # Perform the creation
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return self.custom_response(
#             status.HTTP_201_CREATED,
#             "created successfully",
#             serializer.data,
#             headers=headers
#         )



        
class AttendanceDetailView(BaseLocationViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class UserAttendanceListView(generics.GenericAPIView):
    serializer_class = AttendanceSerializer

    def get(self, request, course_id, registration_id, *args, **kwargs):
        try:
            attendance_records = Attendance.objects.filter(
                student_id=registration_id, course_id=course_id
            )
            serializer = self.get_serializer(attendance_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AttendanceFilterViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    # Specify fields for filtering
    filterset_fields = ['date', 'course']

    def list(self, request, *args, **kwargs):
        # Custom response for the list
        response = super().list(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_200_OK, "Filtered attendance records fetched successfully", response.data
        )


class SessionsAPIViewAttendance(APIView):
    def get(self, request, session_id):
        try:
            # Fetch the session to ensure it exists
            session = Sessions.objects.get(id=session_id)

            # Get all students linked to this session via StudentSession
            student_sessions = StudentSession.objects.filter(session=session)

            # Serialize the student session data
            student_serializer = StudentDetailAttendanceSerializer(student_sessions, many=True)

            # Get the instructor associated with this session from InstructorSession
            try:
                instructor_session = InstructorSession.objects.get(session=session)
                instructor = instructor_session.instructor

                # Get the instructor's user details and construct full name
                if instructor and instructor.id:
                    full_name = f"{instructor.id.first_name} {instructor.id.last_name}".strip()
                else:
                    full_name = None
            except InstructorSession.DoesNotExist:
                full_name = None
            except User.DoesNotExist:
                full_name = None

            # Return the response with student and instructor data
            return Response({
                "status_code": status.HTTP_200_OK,
                "message": "Students and instructor fetched successfully.",
                "data": {
                    "students": student_serializer.data,
                    "instructor": full_name
                }
            }, status=status.HTTP_200_OK)

        except Sessions.DoesNotExist:
            return Response({
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": f"Session with ID {session_id} not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)


# class SessionsAPIViewAttendance(APIView):
#     def get(self, request, session_id):
#         try:
#             # Fetch the session to ensure it exists
#             session = Sessions.objects.get(id=session_id)
#             # Get all students linked to this session via StudentSession
#             student_sessions = StudentSession.objects.filter(session=session)
#             # Serialize the student session data
#             serializer = StudentDetailAttendanceSerializer(student_sessions, many=True)
#             return Response({
#                 "status_code": status.HTTP_200_OK,
#                 "message": "Students fetched successfully.",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)
#         except Sessions.DoesNotExist:
#             return Response({
#                 "status_code": status.HTTP_404_NOT_FOUND,
#                 "message": f"Session with ID {session_id} not found.",
#                 "data": None
#             }, status=status.HTTP_404_NOT_FOUND)


class StudentAttendanceListView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id,*args, **kwargs):
        student = request.user.student
        print(student)
        attendances = Attendance.objects.filter(student=student,course_id=course_id)
        print(attendances)
        serialized_attendance = AttendanceSerializer(attendances, many=True)
        
        response_data = {
            "attendance": serialized_attendance.data
        }
        
        return self.custom_response(
            status.HTTP_200_OK, "Student attendance retrieved successfully", response_data
        )


class InstructorAttendanceView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id, course_id=None, *args, **kwargs):
        date_filter = request.query_params.get('date', None)
        
        # Get students for the session
        students = Student.objects.filter(studentsession__session_id=session_id)
   
        # Filter attendance by course and date if provided 
        attendances = Attendance.objects.filter(student__in=students)
        
        if date_filter:
            attendances = attendances.filter(date=date_filter)
        
        serialized_attendance = AttendanceSerializer(attendances, many=True)
        
        response_data = {
            "attendance": serialized_attendance.data
        }
        
        return self.custom_response(
            status.HTTP_200_OK, "Students' attendance retrieved successfully", response_data
        )


    def post(self, request, session_id, course_id, *args, **kwargs):
        try:
            session = Sessions.objects.get(id=session_id, course__id=course_id)
        except Sessions.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND, "Session not found", {}
            )

        # Retrieve all students enrolled in the session
        enrolled_students = Student.objects.filter(
            studentsession__session=session
        )

        attendance_data = []
        current_date = timezone.now().date()
        marked_by_name = f"{request.user.first_name} {request.user.last_name}".strip()
        # Iterate through the incoming request data
        for attendance_entry in request.data:
            student_id = attendance_entry.get("student")
            student_status = attendance_entry.get("status", 0)  # Changed from status to student_status
            marked_by = attendance_entry.get("marked_by", marked_by_name)

            # Ensure the student exists in the session
            try:
                student = enrolled_students.get(registration_id=student_id)
            except Student.DoesNotExist:
                continue  # Skip if student not found

            attendance_data.append(
                Attendance(
                    student=student,
                    course_id=course_id,
                    status=student_status,
                    marked_by=marked_by,
                    date=current_date
                )
            )

        # Bulk create attendance records
        created_attendance = Attendance.objects.bulk_create(attendance_data)

        # Serialize the created attendance records
        serialized_data = AttendanceSerializer(created_attendance, many=True).data

        return self.custom_response(
            status.HTTP_201_CREATED, "Attendance marked successfully", serialized_data
        )


class AdminAttendanceView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id, *args, **kwargs):
        date_filter = request.query_params.get('date', None)
        
        try:
            # Filter students based on session ID
            students_in_session = Student.objects.filter(studentsession__session__id=session_id)
            print(students_in_session)
        except Student.DoesNotExist:
            return Response({"detail": "No students found for this session."}, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch attendance records for students in the session
        attendances = Attendance.objects.filter(student__in=students_in_session)
        
        if date_filter:
            attendances = attendances.filter(date=date_filter)
        
        serialized_attendance = AttendanceSerializer(attendances, many=True)
        
        response_data = {
            "attendance": serialized_attendance.data
        }
        
        return self.custom_response(
            status.HTTP_200_OK, "Attendance retrieved successfully for the session", response_data
        )



class InstructorsByCourseAPIView(APIView):
    def get(self, request, course_id, *args, **kwargs):
        # Retrieve instructor sessions for the specified course_id
        instructor_sessions = InstructorSession.objects.filter(session__course_id=course_id)

        if not instructor_sessions.exists():
            return Response({
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "No instructors found for this course.",
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the instructor session data
        serializer = InstructorSessionSerializer(instructor_sessions, many=True)

        return Response({
            "status_code": status.HTTP_200_OK,
            "message": "Instructors fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
