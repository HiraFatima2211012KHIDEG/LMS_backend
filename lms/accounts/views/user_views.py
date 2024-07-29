from rest_framework import (
    views,
    status,
    generics,
    permissions
    )
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from django.contrib.auth import login as auth_login, logout as auth_logout
from ..serializers.user_serializers import (
    UserSerializer,
    AuthTokenSerializer
)
from drf_spectacular.utils import extend_schema
from ..models.models_ import AccessControl
import constants
from django.contrib.auth.models import Group


def get_group_permissions(group_id):
    """Retrieve all the permissions related to a user group"""
    permissions_dict = {}
    access_controls = AccessControl.objects.filter(group_id=group_id)

    for access_control in access_controls:
        model_name = access_control.model
        permissions_value = ''

        if access_control.create:
            permissions_value += constants.CREATE
        if access_control.read:
            permissions_value += constants.READ
        if access_control.update:
            permissions_value += constants.UPDATE
        if access_control.delete:
            permissions_value += constants.DELETE

        permissions_dict[model_name] = permissions_value

    return permissions_dict



class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class LoginView(views.APIView):
    """View to login a user and start a session."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            group = user.groups.get()
            print(f'group: ', group.id)
            auth_login(request, user)
            temp = get_group_permissions(3)
            print (temp)
            return Response({'message': 'Login successful', 'user_id': user.id, 'response': temp})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    """View to logout a user."""

    @extend_schema(request=None, responses=UserSerializer)
    def post(self, request):
        auth_logout(request)
        return Response({'message': 'Logout successful'})