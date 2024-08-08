from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from ..models.attendance_models import Attendance
from ..serializers.attendance_serializers import AttendanceSerializer
from .location_views import BaseLocationViewSet

class AttendanceListCreateView(BaseLocationViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceDetailView(BaseLocationViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class UserAttendanceListView(generics.GenericAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            attendance_records = Attendance.objects.filter(student_id=user_id)
            serializer = self.get_serializer(attendance_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)