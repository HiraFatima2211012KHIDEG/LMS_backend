from rest_framework import (
    views,
    status,
    generics,
    permissions
    )
from rest_framework.response import Response
from ..serializers.user_serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema
from ..serializers.user_serializers import (
    UserSerializer,
)
from ..models.models_ import AccessControl
import constants





class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'User created successfully',
            'response' : serializer.data
        })


class UserLoginView(views.APIView):
    """
    View to handle user login and generate authentication tokens.
    """
    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: 'Login Successful.',
            400: 'Bad Request.',
            401: 'Unauthorized.',
        }
    )


    def post(self, request):
        """
        Handle POST requests for user login.

        This method processes the login request by validating the provided credentials.
        If valid, it authenticates the user and generates authentication tokens.

        Args:
            request (Request): The HTTP request object containing the login data.

        Returns:
            Response: A Response object with authentication tokens if successful,
                      or error details if validation fails.
        """
        data = request.data
        if 'email' not in data:
            return Response(
                {'status_code' : status.HTTP_400_BAD_REQUEST,
                 'message' : 'Email is not provided.'}
                 )
        if 'password' not in data:
            return Response(
                {'status_code' : status.HTTP_400_BAD_REQUEST,
                 'message' : 'Password is not provided.'}
                 )
        data['email'] = data.get('email', '').lower()
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(
                email=serializer.validated_data["email"], password=serializer.validated_data["password"]
            )
            if user is not None:
                tokens = self.get_tokens_for_user(user)
                user_group_id = Group.objects.get(user = user.id).id
                permission = self.get_group_permissions(user_group_id)
                return Response({
                        'status_code' : status.HTTP_200_OK,
                        'message': 'Login Successful.',
                        'response' : {
                            'token' : tokens,
                            'permissions' : permission
                        }
                        })
            else:
                return Response({
                        'status_code' : status.HTTP_401_UNAUTHORIZED,
                        'message': 'Invalid credentials.'
                        },
                )
        return Response({
                        'status_code' : status.HTTP_400_BAD_REQUEST,
                        'message': 'Unable to login.',
                        'response' : serializer.errors

        })

    def get_tokens_for_user(self, user):
        """
        Generate JWT tokens for the authenticated user.

        Args:
            user (User): The authenticated user object.

        Returns:
            dict: A dictionary containing the refresh and access tokens.
        """
        try:
            refresh = RefreshToken.for_user(user)
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        except Exception as e:
            raise Exception(f"Error generating tokens: {str(e)}")

    def get_group_permissions(self, group_id):
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
            if access_control.remove:
                permissions_value += constants.DELETE

            permissions_dict[model_name] = permissions_value

        return permissions_dict



class UserProfileView(views.APIView):
    """
    View to handle retrieving the authenticated user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Handle GET requests to retrieve user profile.

        This method retrieves the profile of the authenticated user.

        Args:
            request (Request): The HTTP request object containing user data.

        Returns:
            Response: A Response object with the serialized user profile data if successful,
                      or error details if an exception occurs.
        """
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response({
            'status_code': status.HTTP_200_OK,
            'message': 'User profile fetched successfully.',
            'response': serializer.data
        })

class UserProfileUpdateView(views.APIView):
    """
    View to handle updating the authenticated user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        """
        Handle PATCH requests to update user profile.

        Args:
            request (Request): The HTTP request object containing user data.

        Returns:
            Response: A Response object with the updated user profile data if successful,
                      or error details if validation fails.
        """
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                        'status_code' : status.HTTP_200_OK,
                        'message': 'User updated successfully.',
            })


class ChangePasswordView(views.APIView):
    """
    View to change the password of the authenticated user.

    * Requires authentication.
    * Validates the old password and ensures the new password meets complexity requirements.
    * Updates the user's password if validation is successful.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Handle the POST request to change the user's password.

        Parameters:
        request (Request): The request object containing the old and new passwords.

        Returns:
        Response: A response indicating the success or failure of the password change.
        """
        user = request.user
        data = request.data
        if 'old_password' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Old password is not provided.'})
        if 'password' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Password is not provided.'})
        if 'password2' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Confirm password is not provided.'})

        serializer = ChangePasswordSerializer(data=data, context={'user': user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                        'status_code' : status.HTTP_200_OK,
                        'message': 'Password changed successfully.',
                        # 'response' : serializer.data

        }, status=status.HTTP_200_OK)
        else:
            return Response({
                        'status_code' : status.HTTP_400_BAD_REQUEST,
                        'message': 'Unable to change password.',
                        'response' : serializer.errors
        })


class SetPasswordView(views.APIView):
    """
    View to set a new password for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Handle POST request to set a new password.
        """
        user = request.user
        data = request.data
        if 'password' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Password is not provided.'})
        if 'password2' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Confirm password is not provided.'})

        serializer = SetPasswordSerializer(data=data, context={'user': user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                        'status_code' : status.HTTP_200_OK,
                        'message': 'Password set successfully.',
        })
        else:
            return Response({
                        'status_code' : status.HTTP_400_BAD_REQUEST,
                        'message': 'Unable to set password.',
                        'response' : serializer.errors

        })


class ResetPasswordView(views.APIView):
    """
    API view for requesting a password reset email.
    """

    def post(self, request):
        """
        Handle POST request to initiate password reset process.

        Args:
            request: The HTTP request object containing the email.

        Returns:
            Response: JSON response with a success message or validation errors.
        """
        data = request.data
        if 'email' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Email is not provided.'})


        serializer = ResetPasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {
                        'status_code' : status.HTTP_200_OK,
                        'message': 'Password reset link sent. Please check your email.',
        }
            )
        return Response(
            {
                        'status_code' : status.HTTP_400_BAD_REQUEST,
                        'message': 'Unable to set password.',
                        'response' : serializer.errors

        }
        )


class UserpasswordResetView(views.APIView):
    """
    API View for resetting a user's password.

    Handles POST requests to reset the password using a UID and token.
    """

    def post(self, request, **kwargs):
        """
        Handle the password reset process.

        Args:
            request (Request): The incoming request object.
            **kwargs: Arbitrary keyword arguments, including 'uid' and 'token'.

        Returns:
            Response: A response indicating the success or failure of the password reset.
        """
        uid = kwargs.get("uid")
        token = kwargs.get("token")
        data = request.data
        if 'password' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Password is not provided.'})
        if 'password2' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Confirm password is not provided.'})


        if not uid or not token:
            return Response({
                        'status_code' : status.HTTP_400_BAD_REQUEST,
                        'message': 'UID and token are required.',

        })

        try:
            serializer = UserpasswordResetSerializer(
                data=data, context={"uid": uid, "token": token}
            )

            if serializer.is_valid(raise_exception=True):
                return Response(
                       {
                        'status_code' : status.HTTP_200_OK,
                        'message': 'Password reset successfully.',
                       }
                )

            return Response(
                   {
                        'status_code' : status.HTTP_400_BAD_REQUEST,
                        'message': 'Unable to set password.',
                        'response' : serializer.errors
        }
            )

        except DjangoUnicodeDecodeError:
            return Response(        {
                        'status_code' : status.HTTP_400_BAD_REQUEST,
                        'message': 'Invalid UID or token.',
        })
