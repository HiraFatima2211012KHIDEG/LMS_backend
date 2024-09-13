"""
Views for the Accounts Applications API.
"""

from rest_framework import viewsets
from rest_framework import generics
from ..serializers.application_serializers import (
    ApplicationSerializer,
    TechSkillSerializer,
)
from ..serializers.location_serializers import *
from rest_framework import views, status, generics, permissions
from ..serializers.user_serializers import *
from accounts.models import *
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from ..models.user_models import TechSkill
from django.db import transaction
from accounts.utils import send_email
from django.core.signing import TimestampSigner
import base64
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from .location_views import CustomResponseMixin
from course.serializers import *
from django.db.models import Q
from utils.custom import custom_extend_schema
from ..models.location_models import *


class CreateApplicationView(generics.CreateAPIView):
    """Create a new user in the application."""

    serializer_class = ApplicationSerializer

    def perform_create(self, serializer):
        email = serializer.validated_data.get("email").lower()
        city = serializer.validated_data.get("city").title()
        city_abb = serializer.validated_data.get("city_abb").upper()
        first_name = serializer.validated_data.get("first_name").title()
        last_name = serializer.validated_data.get("last_name").title()
        group_name = serializer.validated_data.get("group_name").lower()
        serializer.save(
            email=email,
            city=city,
            city_abb=city_abb,
            first_name=first_name,
            last_name=last_name,
            group_name=group_name,
        )


# class EmailVerificationToken(AccessToken):
#     lifetime = timedelta(minutes=10)

#     @classmethod
#     def for_application(cls, application):
#         token = cls()
#         token['user_id'] = application.id  # Store application ID
#         token['user_email'] = application.email  # Store application email
#         return token


class ApplicationProcessView(views.APIView, CustomResponseMixin):
    """View to handle application status"""

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="group_name",
                description="Filter by group_name of user.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="status",
                description="Filter by status of application.",
                required=False,
                type=str,
            ),
        ],
        responses={200: "application/json"},
    )
    def get(self, request, filteration_id=None):
        if filteration_id is None:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "filteration_id is not provided.", None
            )

        group_name = request.query_params.get("group_name")
        application_status = request.query_params.get("status")

        if application_status not in ["pending", "short_listed", "approved", "removed"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid status. Choices are 'pending', 'approved', 'short_listed', 'removed'.",
                None,
            )

        if group_name not in ["student", "instructor"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid group_name. Choices are 'student' and 'instructor'.",
                None,
            )

        try:
            if application_status == "approved" and group_name == "student":
                specific_program = StudentApplicationSelection.objects.filter(
                    selected_program_id=filteration_id
                )
                print("a", specific_program)
                specific_program_list = list(
                    specific_program.values_list("application_id", flat=True)
                )
                print("list", specific_program_list)
                applications = Applications.objects.filter(
                    id__in=specific_program_list,
                    group_name=group_name,
                    application_status=application_status,
                )
                print("app", applications)

            elif application_status == "approved" and group_name == "instructor":
                specific_skills = InstructorApplicationSelection.objects.filter(
                    selected_skills__id=filteration_id
                ).distinct()
                print("a", specific_skills)
                specific_skills_list = list(
                    specific_skills.values_list("application_id", flat=True)
                )
                print("list", specific_skills_list)
                applications = Applications.objects.filter(
                    id__in=specific_skills_list,
                    group_name=group_name,
                    application_status=application_status,
                )
                print("app", applications)

            # Query the applications based on the provided filteration_id and group_name
            else:
                applications = Applications.objects.filter(
                    Q(
                        program__id=filteration_id,
                        group_name=group_name,
                        application_status=application_status,
                    )
                    | Q(
                        required_skills__id=filteration_id,
                        group_name=group_name,
                        application_status=application_status,
                    )
                ).distinct()

            if not applications.exists():
                return self.custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "No applications found for the provided program ID, group_name, and status.",
                    None,
                )

            serialized_data = ApplicationSerializer(applications, many=True).data
            # Handle applications based on the group_name
            if group_name == "student":
                self.handle_student_applications(serialized_data, application_status)
            elif group_name == "instructor":
                self.handle_instructor_applications(serialized_data, application_status)

            return self.custom_response(
                status.HTTP_200_OK,
                "Applications fetched successfully.",
                serialized_data,
            )

        except Exception as e:
            # Catch any unexpected exceptions and log them if necessary
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred: {str(e)}",
                None,
            )

    def handle_student_applications(self, serialized_data, application_status):
        """Handle processing of student applications based on their status."""
        for application in serialized_data:
            programs = application.pop("program", [])
            locations = application.pop("location", [])

            if application_status == "approved":
                try:
                    selected_user = StudentApplicationSelection.objects.get(
                        application_id=application["id"]
                    )
                    selected_program = Program.objects.get(
                        id=selected_user.selected_program.id
                    )
                    selected_location = Location.objects.get(
                        id=selected_user.selected_location.id
                    )
                    application["program"] = [ProgramSerializer(selected_program).data]
                    application["location"] = [
                        LocationSerializer(selected_location).data
                    ]
                except StudentApplicationSelection.DoesNotExist:
                    application["program"] = None  # or handle the case appropriately
                    application["location"] = None
            else:
                complete_related_programs = Program.objects.filter(id__in=programs)
                application["program"] = [
                    {"id": program["id"], "name": program["name"]}
                    for program in ProgramSerializer(
                        complete_related_programs, many=True
                    ).data
                ]
                complete_related_locations = Location.objects.filter(id__in=locations)
                # application["location"] = application.get("location", None)
                application["location"] = [
                    {"id": location["id"], "name": location["name"]}
                    for location in LocationSerializer(
                        complete_related_locations, many=True
                    ).data
                ]

    def handle_instructor_applications(self, serialized_data, application_status):
        """Handle processing of instructor applications based on their status."""
        for application in serialized_data:
            related_skills = application.pop("required_skills", [])
            related_locations = application.pop("location", [])

            if application_status == "approved":
                try:
                    selected_user = InstructorApplicationSelection.objects.get(
                        application_id=application["id"]
                    )
                    selected_skills = selected_user.selected_skills.all()
                    application["skill"] = TechSkillSerializer(
                        selected_skills, many=True
                    ).data
                    selected_locations = selected_user.selected_locations.all()
                    application["location"] = LocationSerializer(
                        selected_locations, many=True
                    ).data
                except InstructorApplicationSelection.DoesNotExist:
                    application["skill"] = []  # or handle the case appropriately
                    application["location"] = []
            else:
                # Check if related_skills is a list of integers or dictionaries
                if (related_skills and isinstance(related_skills[0], dict)) and (
                    related_locations and isinstance(related_locations[0], dict)
                ):
                    # related_skills is a list of dictionaries
                    related_skills_objects = TechSkill.objects.filter(
                        id__in=[skill["id"] for skill in related_skills]
                    )
                    related_locations_objects = Location.objects.filter(
                        id__in=[location["id"] for location in related_locations]
                    )
                else:
                    # related_skills is a list of integers
                    related_skills_objects = TechSkill.objects.filter(
                        id__in=related_skills
                    )
                    related_locations_objects = Location.objects.filter(
                        id__in=related_locations
                    )

                application["skill"] = TechSkillSerializer(
                    related_skills_objects, many=True
                ).data
                application["location"] = LocationSerializer(
                    related_locations_objects, many=True
                ).data

        # # Handle location similarly to skills
        # if related_locations and isinstance(related_locations[0], dict):
        #     # related_locations is a list of dictionaries
        #     related_locations_objects = Location.objects.filter(
        #         id__in=[loc["id"] for loc in related_locations]
        #     )
        # else:
        #     # related_locations is a list of integers
        #     related_locations_objects = Location.objects.filter(
        #         id__in=related_locations
        #     )

        # application["location"] = LocationSerializer(
        #     related_locations_objects, many=True
        # ).data

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="application_id",
                description="Filter by group_name of user.",
                required=False,
                type=str,
            )
        ],
        responses={200: "application/json"},
    )
    @custom_extend_schema(ApplicationSerializer)
    def patch(self, request, filteration_id=None):
        data = request.data
        application_id = request.query_params.get("application_id")

        if not application_id:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Application ID is not provided.", None
            )

        if "application_status" not in data:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Application status is not provided.", None
            )

        try:
            application_obj = Applications.objects.get(id=application_id)
        except Applications.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No application object found for this application ID.",
                None,
            )

        application_status = data.get("application_status").lower()
        if application_status not in ["short_listed", "approved", "removed"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Invalid application status.", None
            )

        try:
            with transaction.atomic():
                serializer = ApplicationSerializer(
                    application_obj,
                    data={"application_status": application_status},
                    partial=True,
                )
                if serializer.is_valid(raise_exception=True):
                    if application_status in ["short_listed", "removed"]:
                        serializer.save()
                        return self.custom_response(
                            status.HTTP_200_OK,
                            f"Application status has been changed to {application_status}.",
                            serializer.data,
                        )

                    elif application_status == "approved":
                        email_content = ""
                        if application_obj.group_name == "student":
                            program_id = data.get("program_id")
                            location_id = data.get("location_id")
                            if program_id is None:
                                return self.custom_response(
                                    status.HTTP_400_BAD_REQUEST,
                                    "Selected program_id is not provided.",
                                    None,
                                )
                            if location_id is None:
                                return self.custom_response(
                                    status.HTTP_400_BAD_REQUEST,
                                    "Selected location_id is not provided.",
                                    None,
                                )                               
                            try:
                                program = Program.objects.get(id=program_id)
                                location = Location.objects.get(id=location_id)
                            except Program.DoesNotExist:
                                return self.custom_response(
                                    status.HTTP_404_NOT_FOUND,
                                    "No program object found for this ID.",
                                    None,
                                )
                            except Location.DoesNotExist:
                                return self.custom_response(
                                    status.HTTP_404_NOT_FOUND,
                                    "No location object found for this ID.",
                                    None,
                                )                                

                            related_programs = application_obj.program.all()

                            if program not in related_programs:
                                return self.custom_response(
                                    status.HTTP_400_BAD_REQUEST,
                                    f"Invalid program_id.",
                                    None,
                                )
                            related_locations = application_obj.location.all()    
                            if location not in related_locations:
                                return self.custom_response(
                                    status.HTTP_400_BAD_REQUEST,
                                    f"Invalid location_id.",
                                    None,
                                )                                    

                            StudentApplicationSelection.objects.create(
                                application=application_obj, selected_program=program, selected_location=location
                            )

                            # Customize email body for students
                            email_content = (
                                f"Congratulations {application_obj.first_name} {application_obj.last_name}!\n\n"
                                f"You have been selected for the program '{program.name}' "
                                f"at the location '{location.name} Center'.\n\n"
                                f"Please complete your selection process by verifying your account using the link below."
                            )

                        elif application_obj.group_name == "instructor":
                            skills_ids = data.get("skills_id", [])
                            location_ids = data.get("locations_id", [])
                            if not skills_ids or not set(skills_ids).issubset(
                                application_obj.required_skills.values_list(
                                    "id", flat=True
                                )
                            ):
                                return self.custom_response(
                                    status.HTTP_400_BAD_REQUEST,
                                    "Selected skills_id is not provided or Invalid skills_id found.",
                                    None,
                                )

                            if not location_ids or not set(location_ids).issubset(
                                application_obj.location.values_list(
                                    "id", flat=True
                                )
                            ):
                                return self.custom_response(
                                    status.HTTP_400_BAD_REQUEST,
                                    "Selected location_id is not provided or Invalid location_id found.",
                                    None,
                                )

                            skills = TechSkill.objects.filter(id__in=skills_ids)
                            locations = Location.objects.filter(id__in=location_ids)
                            instructor_selection = (
                                InstructorApplicationSelection.objects.create(
                                    application=application_obj
                                )
                            )

                            instructor_selection.selected_skills.set(skills)
                            instructor_selection.selected_locations.set(locations)

                            # Customize email body for instructors
                            selected_skills_list = ', '.join([skill.name for skill in skills])
                            selected_locations_list = ', '.join([f"{location.name} Center" for location in locations])
                            email_content = (
                                f"Congratulations {application_obj.first_name} {application_obj.last_name}!\n\n"
                                f"You have been selected as an instructor for the following skills:\n"
                                f"- Skills: {selected_skills_list}\n"
                                f"- Locations: {selected_locations_list}\n\n"
                                f"Please complete your selection process by verifying your account using the link below."
                            )

                        # Generate verification link and send email
                        token = self.create_signed_token(
                            application_id, application_obj.email
                        )
                        verification_link = (
                            f"http://localhost:3000/auth/account-verify/{str(token)}"
                        )
                        body = f"{email_content}\n\nVerification Link:\n{verification_link}\n\nThis link will expire in 3 days."

                        email_data = {
                            "email_subject": "Verify your account",
                            "body": body,
                            "to_email": application_obj.email,
                        }
                        send_email(email_data)

                        serializer.save()
                        return self.custom_response(
                            status.HTTP_200_OK,
                            f"Application status has been changed to {application_status}.",
                            serializer.data,
                        )
        except Exception as e:
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred while processing the application: {str(e)}",
                None,
            )


    def create_signed_token(self, id, email):
        signer = TimestampSigner()
        # Combine the user_id and email into a single string
        data = f"{id}:{email}"
        # Encode the data with base64
        encoded_data = base64.urlsafe_b64encode(data.encode()).decode()
        # Sign the encoded data
        signed_token = signer.sign(encoded_data)
        return signed_token


class VerifyEmailandSetPasswordView(views.APIView, CustomResponseMixin):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "Verification token received via email",
                    },
                    "password": {
                        "type": "string",
                        "description": "New password to set for the user",
                    },
                    "password2": {
                        "type": "string",
                        "description": "Confirm new password to set for the user",
                    },
                },
                "required": ["token", "password", "password2"],
            }
        },
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        description="Verifies the user's email and sets a password.",
    )
    def post(self, request):
        token = request.data.get("token")
        password = request.data.get("password")
        password2 = request.data.get("password2")
        if not token:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Token is required.", None
            )
        if not password:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "password is required.", None
            )
        if not password2:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Confirm password is required.", None
            )

        signer = TimestampSigner()
        try:
            with transaction.atomic():
                # Verify the token
                # token = EmailVerificationToken(token_str)
                # print(token)
                # user_id = token['user_id']
                # user_email = token.get('user_email')
                # print(user_email)
                # Check if user already exists
                unsigned_data = signer.unsign(token, max_age=3600)
                decoded_data = base64.urlsafe_b64decode(unsigned_data).decode()
                print(decoded_data)
                user_id, email = decoded_data.split(":")
                existing_user = get_user_model().objects.filter(email=email).first()
                if existing_user:
                    return self.custom_response(
                        status.HTTP_400_BAD_REQUEST, "User already verified", None
                    )

                # Retrieve the application and create a user
                application = Applications.objects.get(id=user_id)
                user_data = {
                    "email": application.email,
                    "first_name": application.first_name,
                    "last_name": application.last_name,
                    "contact": application.contact,
                    "city": application.city,
                    "is_verified": True,
                }
                user = get_user_model().objects.create_user(**user_data)

                # Create StudentInstructor record based on group_name
                if application.group_name == "student":
                    try:
                        selected_student_program = (
                            StudentApplicationSelection.objects.get(
                                application=application
                            ).selected_program
                        )
                    except StudentApplicationSelection.DoesNotExist:
                        return self.custom_response(
                            status.HTTP_400_BAD_REQUEST,
                            "Program selection not found for the application.",
                            None,
                        )
                    program_name = selected_student_program.program_abb
                    city_abb = application.city_abb
                    year = str(application.year)[-2:]
                    month = application.created_at.month
                    category = None
                    if month in [9, 10, 11]:
                        category = "Fall"
                    elif month in [12, 1, 2]:
                        category = "Winter"
                    elif month in [3, 4, 5]:
                        category = "Spring"
                    elif month in [6, 7, 8]:
                        category = "Summer"
                    else:
                        category = "Annual"

                    batch = f"{city_abb.upper()}-{year}-{category[:3]}-{program_name}"
                    Student.objects.create(
                        user=user, registration_id=f"{batch}-{user.id}"
                    )
                elif application.group_name == "instructor":
                    # Handle instructor logic if needed
                    Instructor.objects.create(id=user)
                else:
                    return self.custom_response(
                        status.HTTP_400_BAD_REQUEST, "Invalid group_name.", None
                    )

                # Set the password using SetPasswordSerializer
                password_data = {"password": password, "password2": password2}
                serializer = SetPasswordSerializer(
                    data=password_data, context={"user": user}
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                else:
                    return self.custom_response(
                        status.HTTP_400_BAD_REQUEST,
                        "Verification failed.",
                        serializer.errors,
                    )

                return self.custom_response(
                    status.HTTP_200_OK,
                    "Email verified and user created successfully.",
                    serializer.data,
                )

        except SignatureExpired:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "The reset link has expired.", None
            )
        except BadSignature:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid token or data tampering detected.",
                None,
            )

        except Applications.DoesNotExist:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "User not found.", None
            )


class ResendVerificationEmail(views.APIView, CustomResponseMixin):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request):
        email = request.data.get("email")
        try:
            applicant = Applications.objects.get(email=email)
            if applicant.application_status != "approved":
                return self.custom_response(
                    status.HTTP_400_BAD_REQUEST,
                    "You are not a selected user, contact admin in case of any confusion.",
                    None,
                )
            existing_user = get_user_model().objects.filter(email=email).first()
            if existing_user and existing_user.is_verified:
                return self.custom_response(
                    status.HTTP_400_BAD_REQUEST, "User already verified", None
                )

            token = self.create_signed_token(applicant.id, applicant.email)
            verification_link = (
                f"http://localhost:3000/auth/account-verify/{str(token)}"
            )
            print(token)
            body = (
                f"Congratulations {applicant.first_name} {applicant.last_name}!\n"
                f"You are requested to complete the selection process by verifying your account. "
                f"Please click the following link to proceed.\n{verification_link}"
            )

            email_data = {
                "email_subject": "Verify your account",
                "body": body,
                "to_email": email,
            }
            send_email(email_data)

            return self.custom_response(
                status.HTTP_200_OK, "Verification email resent.", None
            )

        except Applications.DoesNotExist:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Application with this email does not exist.",
                None,
            )

    def create_signed_token(self, id, email):
        signer = TimestampSigner()
        # Combine the user_id and email into a single string
        data = f"{id}:{email}"
        # Encode the data with base64
        encoded_data = base64.urlsafe_b64encode(data.encode()).decode()
        # Sign the encoded data
        signed_token = signer.sign(encoded_data)
        return signed_token


# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework import views
# from django.contrib.auth import get_user_model
# from django.db import transaction

# class UserRegistrationView(views.APIView):
#     # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

#     def post(self, request):
#         data = request.data
#         user_id = data.get('user_id')
#         session_id = data.get('session_id')

#         if not user_id or not session_id:
#             return Response({
#                 'status_code': status.HTTP_400_BAD_REQUEST,
#                 'message': 'User ID and Session ID are required.'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             with transaction.atomic():
#                 user = get_user_model().objects.get(id=user_id)
#                 session = Sessions.objects.get(id=session_id)
#                 serializer = SessionsSerializer(session)
#                 session_data = serializer.data
#                 user_location = session_data.get('location')
#                 location_object = Location.objects.get(id = user_location)
#                 user_location_name = location_object.name
#                 user_batch = session_data.get('batch')
#                 batch_object = Batch.objects.get(batch = user_batch)
#                 user_batch_name = batch_object.batch
#                 user_program = "Computer Science"
#                 link = "{sample link : jab itna kr hi lia hay to link bhi kabhi na kabhi ajaega 🤲}"

#                 student_instructor = StudentInstructor.objects.create(
#                     user=user,
#                     session=session,
#                     batch=batch_object
#                 )

#                 student_instructor_serializer = StudentInstructorSerializer(student_instructor)

#                 # body = (f"Congratulations {user.first_name} {user.last_name}!,\n"
#                 #         f"Welcome to xloop lms.You have been enrolled in {user_program} program with batch no # {user_batch_name}."
#                 #         f"You are requested to attend your classes in {user_location_name} center. "
#                 #         f"Please click the following link to verify your account.\n{link}")

#                 # email_data = {
#                 #     "email_subject": "Verify your account",
#                 #     "body": body,
#                 #     "to_email": user.email,
#                 # }
#                 # send_email(email_data)
#                 print(session, user_location_name, user_batch_name)

#                 return Response({
#                     'status_code': status.HTTP_200_OK,
#                     'message': 'User registered successfully, and email sent.',
#                     'response': {
#                         'student_instructor_id': student_instructor_serializer.data
#                     }
#                 }, status=status.HTTP_200_OK)

#         except get_user_model().DoesNotExist:
#             return Response({
#                 'status_code': status.HTTP_404_NOT_FOUND,
#                 'message': 'User not found.'
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Sessions.DoesNotExist:
#             return Response({
#                 'status_code': status.HTTP_404_NOT_FOUND,
#                 'message': 'Session not found.'
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({
#                 'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 'message': f'An error occurred: {str(e)}'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# views.py


class TechSkillViewSet(viewsets.ModelViewSet):
    queryset = TechSkill.objects.all()
    serializer_class = TechSkillSerializer


class ApplicationStatusCount(views.APIView, CustomResponseMixin):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="group_name",
                description="Filter by group_name of user.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="status",
                description="Filter by status of application.",
                required=False,
                type=str,
            ),
        ],
        responses={200: "application/json"},
    )
    def get(self, request, filteration_id=None):
        if filteration_id is None:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "filteration_id is not provided.",
                None,
            )

        # Get the group_name from the query parameters
        group_name = request.query_params.get("group_name")

        # Validate group_name input
        if group_name not in ["student", "instructor"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid group_name. Choices are 'student' and 'instructor'.",
                None,
            )

        # Get the application status from query parameters
        application_status = request.query_params.get("status", None)

        # Validate status input
        if application_status not in ["pending", "short_listed", "approved", None]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid status. Choices are 'pending', 'approved', 'short_listed'.",
                None,
            )

        try:
            # Base query filtering on filteration_id and group_name
            base_query = Applications.objects.filter(
                Q(program__id=filteration_id, group_name=group_name)
                | Q(required_skills__id=filteration_id, group_name=group_name)
            ).distinct()

            # Filter the base query by the application status if provided
            if application_status:
                count = base_query.filter(application_status=application_status).count()
                return self.custom_response(
                    status.HTTP_200_OK,
                    f"Count for status '{application_status}' fetched successfully.",
                    {application_status: count},
                )

            # If no specific status is provided, get counts for all statuses
            counts = {
                "approved": base_query.filter(application_status="approved").count(),
                "short_listed": base_query.filter(
                    application_status="short_listed"
                ).count(),
                "pending": base_query.filter(application_status="pending").count(),
            }

            # Count of verified accounts: emails exist in both Applications and User and have status 'approved'
            verified_count = base_query.filter(
                email__in=User.objects.values_list("email", flat=True),
                application_status="approved",
            ).count()

            # Count of unverified accounts: emails do not exist in User but have status 'approved'
            unverified_count = base_query.filter(
                ~Q(email__in=User.objects.values_list("email", flat=True)),
                application_status="approved",
            ).count()

            # Add verified and unverified counts to the response data
            counts["verified"] = verified_count
            counts["unverified"] = unverified_count

            return self.custom_response(
                status.HTTP_200_OK,
                "Counts for all statuses fetched successfully.",
                counts,
            )

        except Exception as e:
            # Catch any unexpected exceptions and log them if necessary
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred: {str(e)}",
                None,
            )


# class VerifiedUnverifiedAccountsCountView(views.APIView, CustomResponseMixin):

#     permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

#     def get(self, request, filteration_id=None):
#         if filteration_id is None:
#             return self.custom_response(
#                 status.HTTP_400_BAD_REQUEST, "filteration_id is not provided.", None
#             )

#         status = request.query_params.get('status')
#         if status != "approved":
#             return self.custom_response(
#                 status.HTTP_400_BAD_REQUEST,
#                 "Invalid status",
#                 None,
#             )

#         else:
