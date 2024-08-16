from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *

class WeightageListCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        weightages = Weightage.objects.all()
        serializer = WeightageSerializer(weightages, many=True)
        return Response({
            'message': 'Weightages retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = WeightageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Weightage created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Error creating weightage',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class WeightageDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        weightage = get_object_or_404(Weightage, pk=pk)
        serializer = WeightageSerializer(weightage)
        return Response({
            'message': 'Weightage retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        weightage = get_object_or_404(Weightage, pk=pk)
        serializer = WeightageSerializer(weightage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Weightage updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Error updating weightage',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        weightage = get_object_or_404(Weightage, pk=pk)
        weightage.delete()
        return Response({
            'message': 'Weightage deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)