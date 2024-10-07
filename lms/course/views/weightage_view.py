from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.models import *
from ..serializers import *
from utils.custom import CustomResponseMixin, custom_extend_schema


class WeightageListCreateAPIView(APIView, CustomResponseMixin):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        weightages = Weightage.objects.all()
        serializer = WeightageSerializer(weightages, many=True)
        return self.custom_response(
            status_code=status.HTTP_200_OK,
            message='Weightages retrieved successfully',
            data=serializer.data
        )

    def post(self, request, format=None):
        serializer = WeightageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status_code=status.HTTP_201_CREATED,
                message='Weightage created successfully',
                data=serializer.data
            )
        return self.custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message='Error creating weightage',
            data=serializer.errors
        )

class WeightageDetailAPIView(APIView, CustomResponseMixin):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        weightage = get_object_or_404(Weightage, pk=pk)
        serializer = WeightageSerializer(weightage)
        return self.custom_response(
            status_code=status.HTTP_200_OK,
            message='Weightage retrieved successfully',
            data=serializer.data
        )

    def put(self, request, pk, format=None):
        weightage = get_object_or_404(Weightage, pk=pk)
        serializer = WeightageSerializer(weightage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status_code=status.HTTP_200_OK,
                message='Weightage updated successfully',
                data=serializer.data
            )
        return self.custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message='Error updating weightage',
            data=serializer.errors
        )

    def delete(self, request, pk, format=None):
        weightage = get_object_or_404(Weightage, pk=pk)
        weightage.delete()
        return self.custom_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message='Weightage deleted successfully',
            data=None
        )

class WeightageListByCourseId(APIView, CustomResponseMixin):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, session_id, format=None):
        # Check if the course exists
        if not Course.objects.filter(id=course_id).exists():
            return self.custom_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message='Course with the given ID not found',
                data=None
            )
        
        # Check if the session exists
        if not Sessions.objects.filter(id=session_id).exists():
            return self.custom_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message='Session with the given ID not found',
                data=None
            )

        # If both course and session exist, filter weightages
        weightages = Weightage.objects.filter(course_id=course_id, session_id=session_id)

        if not weightages.exists():
            return self.custom_response(
                status_code=status.HTTP_200_OK,
                message='No weightages found for the given course and session',
                data=None
            )

        serializer = WeightageSerializer(weightages, many=True)
        return self.custom_response(
            status_code=status.HTTP_200_OK,
            message='Courses weightages retrieved successfully',
            data=serializer.data
        )



# Skill Views
class SkillListCreateAPIView(APIView, CustomResponseMixin):

    @custom_extend_schema(SkillSerializer)
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return self.custom_response(
            status_code=status.HTTP_200_OK,
            message='Skills retrieved successfully',
            data=serializer.data
        )

    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status_code=status.HTTP_201_CREATED,
                message='Skill created successfully',
                data=serializer.data
            )
        return self.custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message='Error creating skill',
            data=serializer.errors
        )


class SkillRetrieveUpdateDestroyAPIView(APIView, CustomResponseMixin):
    def get(self, request, pk):
        try:
            skill = Skill.objects.get(pk=pk)
        except Skill.DoesNotExist:
            return self.custom_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message='Skill not found',
                data=None
            )

        serializer = SkillSerializer(skill)
        return self.custom_response(
            status_code=status.HTTP_200_OK,
            message='Skill retrieved successfully',
            data=serializer.data
        )

    def put(self, request, pk):
        try:
            skill = Skill.objects.get(pk=pk)
        except Skill.DoesNotExist:
            return self.custom_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message='Skill not found',
                data=None
            )

        serializer = SkillSerializer(skill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.custom_response(
                status_code=status.HTTP_200_OK,
                message='Skill updated successfully',
                data=serializer.data
            )
        return self.custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message='Error updating skill',
            data=serializer.errors
        )

    def delete(self, request, pk):
        try:
            skill = Skill.objects.get(pk=pk)
        except Skill.DoesNotExist:
            return self.custom_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message='Skill not found',
                data=None
            )

        skill.delete()
        return self.custom_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message='Skill deleted successfully',
            data=None
        )