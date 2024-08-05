"""
Views for the Accounts Applications API.
"""
from rest_framework import generics
from ..serializers.application_serializers import ApplicationSerializer
from ..serializers.location_serializers import *
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
from accounts.models import *
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema
from ..serializers.user_serializers import (
    UserSerializer,
)
from ..models.models_ import AccessControl
import constants
from django.db import transaction
from accounts.utils import send_email

class CreateApplicationView(generics.CreateAPIView):
    """Create a new user in the application."""
    serializer_class = ApplicationSerializer

from django.db import transaction

class ApplicationProcessView(views.APIView):
    """View to handle application status"""
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
                                                                                                # I will provide a method here to get applications based on program.
        applications = Applications.objects.all()
        serializer = ApplicationSerializer(applications, many = True)
        return Response({
            'status_code' : status.HTTP_200_OK,
            'message' : 'All application fetched.',
            'response' : serializer.data
        })



    def patch(self, request, application_id):                                # I will provide a method here to get applications based on program.
        data = request.data
        if 'application_status' not in data: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Application status is not provided.'}, status=status.HTTP_400_BAD_REQUEST)
        # if application_id is None: return Response({'status_code' : status.HTTP_400_BAD_REQUEST, 'message' : 'Application id is not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                application = Applications.objects.get(id=application_id)
                serializer = ApplicationSerializer(application, data={'application_status' : data.get('application_status')}, partial=True)
                
                if serializer.is_valid(raise_exception=True):
                    application_status = data.get('application_status').lower()
                    print(application_status)
                    if application_status != 'approved':
                        print('if working fine')
                        serializer.save()
                        return Response({
                            'status_code': status.HTTP_200_OK,
                            'message': f'Application status has been changed to {application_status}.',
                            'response': serializer.data
                        })
                    else:
                        print('else working')
                        # Create new user and delete application
                        user_data = {
                            'email': application.email,
                            'first_name': application.first_name,
                            'last_name': application.last_name,
                            'contact': application.contact,
                            'city': application.city
                        }
                        user = get_user_model().objects.create_user(**user_data)
                        print('user', user)
                        application.delete()
                        print('delete worked')
                        return Response({
                            'status_code': status.HTTP_200_OK,
                            'message': 'Application accepted and new user created.',
                            'response': UserSerializer(user).data
                        })
                
        except Applications.DoesNotExist:
            return Response({
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'No application object found for this application ID.'
            }, status=status.HTTP_404_NOT_FOUND)
        

from rest_framework import status
from rest_framework.response import Response
from rest_framework import views
from django.contrib.auth import get_user_model
from django.db import transaction

class UserRegistrationView(views.APIView):
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        session_id = data.get('session_id')

        if not user_id or not session_id:
            return Response({
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'User ID and Session ID are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user = get_user_model().objects.get(id=user_id)
                session = Sessions.objects.get(id=session_id)
                serializer = SessionsSerializer(session)
                session_data = serializer.data
                user_location = session_data.get('location')
                location_object = Location.objects.get(id = user_location)
                user_location_name = location_object.name
                user_batch = session_data.get('batch')
                batch_object = Batch.objects.get(batch = user_batch)
                user_batch_name = batch_object.batch
                user_program = "Computer Science"
                link = "{sample link : jab itna kr hi lia hay to link bhi kabhi na kabhi ajaega 🤲}"

                student_instructor = StudentInstructor.objects.create(
                    user=user,
                    session=session,
                    batch=batch_object
                )

                student_instructor_serializer = StudentInstructorSerializer(student_instructor)

                body = (f"Congratulations {user.first_name} {user.last_name}!,\n"
                        f"Welcome to xloop lms.You have been enrolled in {user_program} program with batch no # {user_batch_name}."
                        f"You are requested to attend your classes in {user_location_name} center. "
                        f"Please click the following link to verify your account.\n{link}")
                
                email_data = {
                    "email_subject": "Verify your account",
                    "body": body,
                    "to_email": user.email,
                }
                send_email(email_data)
                print(session, user_location_name, user_batch_name)

                return Response({
                    'status_code': status.HTTP_200_OK,
                    'message': 'User registered successfully, and email sent.',
                    'response': {
                        'student_instructor_id': student_instructor_serializer.data
                    }
                }, status=status.HTTP_200_OK)

        except get_user_model().DoesNotExist:
            return Response({
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Sessions.DoesNotExist:
            return Response({
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'Session not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






        






