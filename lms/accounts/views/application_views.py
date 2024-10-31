"""
Views for the Accounts Applications API.
"""
import os
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

FRONTEND_URL = os.getenv("FRONTEND_URL")


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
                    try:
                        user = User.objects.get(email=application.get('email'))
                        application['account_status'] = 'verified'
                    except User.DoesNotExist:
                        application['account_status'] = 'unverified'

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

                    try:
                        user = User.objects.get(email=application.get('email'))
                        application['account_status'] = 'verified'
                    except User.DoesNotExist:
                        application['account_status'] = 'unverified'

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
                        print("Token",token)
                        verification_link = (
                            f"{FRONTEND_URL}/auth/account-verify/{str(token)}"
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
                unsigned_data = signer.unsign(token, max_age=259200)
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
                    year = application.year
                    month = application.created_at
                    batch_instance = Batch.objects.filter(
                        city_abb=city_abb,
                        year=year,
                        application_start_date__lte=month,
                        start_date__gte=month,
                    ).first()
                    print(batch_instance)
                    if not batch_instance:
                        return self.custom_response(
                            status.HTTP_400_BAD_REQUEST,
                            "No matching batch found for the provided city and year.",
                            None,
                        )
                    registration_id = f"{batch_instance.batch}-{program_name}-{user.id}"
                    Student.objects.create(user=user, registration_id=registration_id)

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

                response_data = serializer.data
                response_data['email'] = user.email

                return self.custom_response(
                    status.HTTP_200_OK,
                    "Email verified and user created successfully.",
                    # serializer.data,
                    response_data
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

    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

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
            print("Resend",token)
            verification_link = (
                f"{FRONTEND_URL}/auth/account-verify/{str(token)}"
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


class TechSkillViewSet(viewsets.ModelViewSet):
    queryset = TechSkill.objects.all()
    serializer_class = TechSkillSerializer


class ApplicationStatusCount(views.APIView, CustomResponseMixin):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_verified_and_unverified_counts(self, approved_applications):

        users = User.objects.all()
        user_emails_verified_status = {user.email: user.is_verified for user in users}

        verified_count = 0
        unverified_count = 0

        for application in approved_applications:
            email = application.application.email
            if user_emails_verified_status.get(email, False):
                verified_count += 1
            else:
                unverified_count += 1

        return verified_count, unverified_count

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

        group_name = request.query_params.get("group_name")

        if group_name not in ["student", "instructor"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid group_name. Choices are 'student' and 'instructor'.",
                None,
            )

        application_status = request.query_params.get("status", None)

        try:
            if group_name == "student":
                base_query = Applications.objects.filter(
                    program__id=filteration_id, group_name="student"
                )

                if application_status:
                    if application_status == "approved":
                        approved_count = StudentApplicationSelection.objects.filter(
                            selected_program__id=filteration_id,
                            application__application_status="approved",
                        ).count()

                        return self.custom_response(
                            status.HTTP_200_OK,
                            f"Count for 'approved' students fetched successfully.",
                            {"approved": approved_count},
                        )

                    count = base_query.filter(
                        application_status=application_status
                    ).count()

                    return self.custom_response(
                        status.HTTP_200_OK,
                        f"Count for status '{application_status}' fetched successfully.",
                        {application_status: count},
                    )

                else:
                    approved_applications = StudentApplicationSelection.objects.filter(
                        selected_program__id=filteration_id,
                        application__application_status="approved",
                    )
                    verified_count, unverified_count = (
                        self.get_verified_and_unverified_counts(approved_applications)
                    )

                    counts = {
                        "approved": approved_applications.count(),
                        "short_listed": base_query.filter(
                            application_status="short_listed"
                        ).count(),
                        "pending": base_query.filter(
                            application_status="pending"
                        ).count(),
                        "verified": verified_count,
                        "unverified": unverified_count,
                    }

                    return self.custom_response(
                        status.HTTP_200_OK,
                        "Counts for all statuses fetched successfully.",
                        counts,
                    )

            elif group_name == "instructor":
                base_query = Applications.objects.filter(
                    required_skills__id=filteration_id, group_name="instructor"
                ).distinct()

                if application_status:
                    if application_status == "approved":
                        approved_count = (
                            InstructorApplicationSelection.objects.filter(
                                application__required_skills__id=filteration_id,
                                application__application_status="approved",
                            )
                            .distinct()
                            .count()
                        )

                        return self.custom_response(
                            status.HTTP_200_OK,
                            f"Count for 'approved' instructors fetched successfully.",
                            {"approved": approved_count},
                        )

                    count = base_query.filter(
                        application_status=application_status
                    ).count()

                    return self.custom_response(
                        status.HTTP_200_OK,
                        f"Count for status '{application_status}' fetched successfully.",
                        {application_status: count},
                    )

                else:
                    approved_applications = (
                        InstructorApplicationSelection.objects.filter(
                            application__required_skills__id=filteration_id,
                            application__application_status="approved",
                        )
                    )
                    verified_count, unverified_count = (
                        self.get_verified_and_unverified_counts(approved_applications)
                    )
                    counts = {
                        "approved": approved_applications.distinct().count(),
                        "short_listed": base_query.filter(
                            application_status="short_listed"
                        ).count(),
                        "pending": base_query.filter(
                            application_status="pending"
                        ).count(),
                        "verified": verified_count,
                        "unverified": unverified_count,
                    }

                    return self.custom_response(
                        status.HTTP_200_OK,
                        "Counts for all statuses fetched successfully.",
                        counts,
                    )

        except Exception as e:
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred: {str(e)}",
                None,
            )

