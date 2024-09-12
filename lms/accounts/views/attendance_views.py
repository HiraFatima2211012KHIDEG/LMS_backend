from rest_framework import generics, filters, viewsets
from rest_framework.response import Response
from rest_framework import status
from ..models.attendance_models import Attendance
from ..serializers.attendance_serializers import AttendanceSerializer
from .location_views import BaseLocationViewSet
from django_filters.rest_framework import DjangoFilterBackend
from utils.custom import CustomResponseMixin
class AttendanceListCreateView(BaseLocationViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    # Specify the fields that can be used for filtering
    filterset_fields = ["student", "date", "course", "marked_by"]

    # Specify the fields that can be searched
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "course__name",
    ]

    def create(self, request, *args, **kwargs):
        user = request.user
        course_id = request.query_params.get('course_id')

        if not course_id:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "course_id query parameter is required.",
                None
            )

        if isinstance(request.data, list):  # Check if data is a list (bulk creation)
            data = request.data
            for item in data:
                item['course'] = course_id
                item['marked_by'] = user.email

            serializer = self.get_serializer(data=data, many=True)
            if serializer.is_valid():
                serializer.save()
                return self.custom_response(
                    status.HTTP_201_CREATED,
                    "Attendances created successfully",
                    serializer.data
                )
            else:
                return self.custom_response(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid data",
                    serializer.errors
                )

        # Single record creation handling
        request.data['marked_by'] = user.email
        request.data['course'] = course_id

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status.HTTP_201_CREATED, "created successfully", serializer.data
            )
        else:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid data",
                serializer.errors
            )
        
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