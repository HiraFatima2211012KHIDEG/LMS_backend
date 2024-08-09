from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
# from ..models.models import Content
from ..serializers import ContentFile,ContentFileSerializer
from accounts.models.user_models import *
import logging

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


class ContentFileListCreateAPIView(CustomResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        content_files = ContentFile.objects.all()
        serializer = ContentFileSerializer(content_files, many=True)
        return self.custom_response(status.HTTP_200_OK, 'Content files retrieved successfully', serializer.data)

    def post(self, request, format=None):
        serializer = ContentFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_201_CREATED, 'Content file created successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error creating content file', serializer.errors)

class ContentFileDetailAPIView(CustomResponseMixin,APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        content_file = get_object_or_404(ContentFile, pk=pk)
        serializer = ContentFileSerializer(content_file)
        return self.custom_response(status.HTTP_200_OK, 'Content file retrieved successfully', serializer.data)

    def put(self, request, pk, format=None):
        content_file = get_object_or_404(ContentFile, pk=pk)
        serializer = ContentFileSerializer(content_file, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(status.HTTP_200_OK, 'Content file updated successfully', serializer.data)
        return self.custom_response(status.HTTP_400_BAD_REQUEST, 'Error updating content file', serializer.errors)
    

    def delete(self, request, pk, format=None):
        content_file = get_object_or_404(ContentFile, pk=pk)
        content_file.delete()
        return self.custom_response(status.HTTP_204_NO_CONTENT, 'Content file deleted successfully', {})
