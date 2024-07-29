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
from ..serializers.user_serializers import *
# (
#     UserSerializer,
#     UserLoginSerializer,
#     UserProfileSerializer
#     # AuthTokenSerializer
# )
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User




class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


# class CreateTokenView(ObtainAuthToken):
#     """Create a new auth token for user."""
#     serializer_class = AuthTokenSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# class LoginView(views.APIView):
#     """View to login a user and start a session."""
#     serializer_class = AuthTokenSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
#     permission_classes = (permissions.AllowAny,)
#     def post(self, request):
#         serializer = AuthTokenSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             auth_login(request, user)
#             return Response({'message': 'Login successful', 'user_id': user.id})
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LogoutView(views.APIView):
#     """View to logout a user."""

#     @extend_schema(request=None, responses=UserSerializer)
#     def post(self, request):
#         auth_logout(request)
#         return Response({'message': 'Logout successful'})


class UserLoginView(views.APIView):
    """
    View to handle user login and generate authentication tokens.
    """

    # @swagger_auto_schema(request_body=UserLoginSerializer)
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
        if 'email' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Email is not provided.'})
        if 'password' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Password is not provided.'})
        data['email'] = data.get('email', '').lower()
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(
                email=serializer.data["email"], password=serializer.data["password"]
            )
            if user is not None:
                tokens = self.get_tokens_for_user(user)
                return Response(tokens, status=status.HTTP_200_OK)
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
        try:
            user_profile = User.objects.get(id=user.id)
            serializer = UserProfileSerializer(user_profile)
            return Response({
                        'status_code' : status.HTTP_200_OK,
                        'message': 'User profile fetched.',
                        'response' : serializer.data

        })
        except User.DoesNotExist:
            return Response({
                        'status_code' : status.HTTP_404_NOT_FOUND,
                        'message': 'User not found.',
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
                        'response' : serializer.data

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

        email = data.get('email', '').lower()
        data['email'] = email

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
            return Response({"detail": "Invalid UID or token."}, status=status.HTTP_400_BAD_REQUEST)
