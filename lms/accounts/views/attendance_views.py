from rest_framework import generics, filters, viewsets
from rest_framework.response import Response
from rest_framework import status
from ..models.attendance_models import Attendance

from .location_views import BaseLocationViewSet
from django_filters.rest_framework import DjangoFilterBackend
from utils.custom import CustomResponseMixin
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from ..models.location_models import Sessions
from ..models.user_models import StudentSession
from rest_framework.views import APIView
from ..serializers.attendance_serializers import AttendanceSerializer,StudentDetailAttendanceSerializer



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
            serializer = StudentDetailAttendanceSerializer(student_sessions, many=True)
            return Response({
                "status_code": status.HTTP_200_OK,
                "message": "Students fetched successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Sessions.DoesNotExist:
            return Response({
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": f"Session with ID {session_id} not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)