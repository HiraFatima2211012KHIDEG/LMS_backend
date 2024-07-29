from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.shortcuts import get_object_or_404
from ..models.models import Content
from ..serializers import ContentSerializer, ContentFile
import logging

logger = logging.getLogger(__name__)


class ContentListCreateAPIView(APIView):
    # permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        contents = Content.objects.all()
        serializer = ContentSerializer(contents, many=True)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Contents retrieved successfully',
            'response': serializer.data
        })

    def post(self, request, format=None):
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            content = serializer.save()
            
            # Handle file uploads
            files = request.FILES.getlist('files')
            for file in files:
                ContentFile.objects.create(content=content, file=file)
            
            return Response({
                'status_code': status.HTTP_201_CREATED,
                'message': 'Content created successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error creating content',
            'response': serializer.errors
        })

class ContentDetailAPIView(APIView):
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, pk, format=None):
        content = get_object_or_404(Content, pk=pk)
        serializer = ContentSerializer(content)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'Content retrieved successfully',
            'response': serializer.data
        })

    def put(self, request, pk, format=None):
        content = get_object_or_404(Content, pk=pk)
        serializer = ContentSerializer(content, data=request.data)
        if serializer.is_valid():
            content = serializer.save()
            
            # Handle file uploads
            ContentFile.objects.filter(content=content).delete()
            files = request.FILES.getlist('files')
            for file in files:
                ContentFile.objects.create(content=content, file=file)
            
            return Response({
                'status_code': status.HTTP_200_OK,
                'message': 'Content updated successfully',
                'response': serializer.data
            })
        return Response({
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Error updating content',
            'response': serializer.errors
        })

    def delete(self, request, pk, format=None):
        content = get_object_or_404(Content, pk=pk)
        content.delete()
        return Response({
            'status_code': status.HTTP_204_NO_CONTENT,
            'message': 'Content deleted successfully',
            'response': {}
        })