from rest_framework import views, viewsets, status, generics, permissions
from rest_framework.response import Response
from ..serializers.user_serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema
from ..serializers.user_serializers import *
from ..models.user_models import Student
import constants
from utils.custom import CustomResponseMixin, custom_extend_schema
from course.models.models import Course
from ..serializers.location_serializers import *
from django.shortcuts import get_object_or_404
from ..serializers.application_serializers import *
from course.serializers import *


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        if "instructor" in user.groups.values_list("name", flat=True):
            Instructor.objects.get_or_create(id=user)

        return Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "User created successfully",
                "response": serializer.data,
            }
        )


class CreateAdminUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    # permission_classes = [permissions.IsAdminUser]


class UserLoginView(views.APIView):
    """
    View to handle user login and generate authentication tokens.
    """

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
            permissions_value = ""
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

    @custom_extend_schema(UserLoginSerializer)
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
        if "email" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Email is not provided.",
                }
            )
        if "password" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password is not provided.",
                }
            )
        data["email"] = data.get("email", "").lower()
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
            if user is not None:
                tokens = self.get_tokens_for_user(user)
                user_group = Group.objects.get(user=user.id)
                permission = self.get_group_permissions(user_group.id)
                user_profile = UserProfileSerializer(user, context={"user": user})
                user_serializer = None
                session_assigned = False

                if user_group.name == "student":
                    student = Student.objects.get(user=user.id)
                    user_serializer = StudentSerializer(student)
                    try:
                        student_sessions = StudentSession.objects.filter(
                            student=student
                        )
                        if student_sessions.exists():
                            session_assigned = True
                    except StudentSession.DoesNotExist:
                        session_assigned = False

                elif user_group.name == "instructor":
                    instructor = Instructor.objects.get(id=user.id)
                    user_serializer = InstructorSerializer(instructor)
                    try:
                        instructor_sessions = InstructorSession.objects.filter(
                            instructor=instructor
                        )
                        if instructor_sessions.exists():
                            session_assigned = True
                    except InstructorSession.DoesNotExist:
                        session_assigned = False

                return Response(
                    {
                        "status_code": status.HTTP_200_OK,
                        "message": "Login Successful.",
                        "response": {
                            "token": tokens,
                            "Group": user_group.name,
                            "User": user_profile.data,
                            "permissions": permission,
                            "user_data": (
                                user_serializer.data if user_serializer else None
                            ),
                            "session": session_assigned,
                        },
                    }
                )
            else:
                return Response(
                    {
                        "status_code": status.HTTP_401_UNAUTHORIZED,
                        "message": "Invalid credentials.",
                    },
                )
        return Response(
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Unable to login.",
                "response": serializer.errors,
            }
        )


class UserSessionAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """
        Handle GET requests to return session data for the authenticated user.
        """
        user = request.user
        user_group = Group.objects.get(user=user.id)
        session_data = []

        if user_group.name == "student":
            student = Student.objects.get(user=user.id)
            try:
                student_sessions = StudentSession.objects.filter(
                    student=student, status=1
                )
                for student_session in student_sessions:
                    session_info = SessionsSerializer(student_session.session).data
                    try:
                        instructor_session = InstructorSession.objects.get(
                            session=student_session.session, status=1
                        )
                        instructor_data = {
                            "instructor_id": instructor_session.instructor.id.id,
                            "instructor_name": f"{instructor_session.instructor.id.first_name} {instructor_session.instructor.id.last_name}",
                        }
                        session_info["instructor"] = instructor_data
                    except InstructorSession.DoesNotExist:
                        session_info["instructor"] = None
                    session_data.append(session_info)
            except StudentSession.DoesNotExist:
                session_data = []

        elif user_group.name == "instructor":
            instructor = Instructor.objects.get(id=user.id)
            try:
                instructor_sessions = InstructorSession.objects.filter(
                    instructor=instructor, status=1
                )
                for instructor_session in instructor_sessions:
                    session_data.append(
                        SessionsSerializer(instructor_session.session).data
                    )
            except InstructorSession.DoesNotExist:
                session_data = []

        return Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "Session data retrieved successfully.",
                "session": session_data if session_data else None,
            }
        )


class UserProfileView(views.APIView):
    """
    View to handle retrieving the authenticated user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    @custom_extend_schema(UserProfileSerializer)
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
        return Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "User profile fetched successfully.",
                "response": serializer.data,
            }
        )


class UserProfileUpdateView(views.APIView):
    """
    View to handle updating the authenticated user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    @custom_extend_schema(UserProfileUpdateSerializer)
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
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "User updated Successfully.",
                }
            )


class ChangePasswordView(views.APIView):
    """
    View to change the password of the authenticated user.

    * Requires authentication.
    * Validates the old password and ensures the new password meets complexity requirements.
    * Updates the user's password if validation is successful.
    """

    permission_classes = [permissions.IsAuthenticated]

    @custom_extend_schema(ChangePasswordSerializer)
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
        if "old_password" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Old password is not provided.",
                }
            )
        if "password" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password is not provided.",
                }
            )
        if "password2" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Confirm password is not provided.",
                }
            )

        serializer = ChangePasswordSerializer(data=data, context={"user": user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "Password changed successfully.",
                    # 'response' : serializer.data
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Unable to change password.",
                    "response": serializer.errors,
                }
            )


class SetPasswordView(views.APIView):
    """
    View to set a new password for the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]

    @custom_extend_schema(SetPasswordSerializer)
    def post(self, request):
        """
        Handle POST request to set a new password.
        """
        user = request.user
        data = request.data
        if "password" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password is not provided.",
                }
            )
        if "password2" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Confirm password is not provided.",
                }
            )

        serializer = SetPasswordSerializer(data=data, context={"user": user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "Password set successfully.",
                }
            )
        else:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Unable to set password.",
                    "response": serializer.errors,
                }
            )


class ResetPasswordView(views.APIView):
    """
    API view for requesting a password reset email.
    """

    @custom_extend_schema(ResetPasswordSerializer)
    def post(self, request):
        """
        Handle POST request to initiate password reset process.

        Args:
            request: The HTTP request object containing the email.

        Returns:
            Response: JSON response with a success message or validation errors.
        """
        data = request.data
        if "email" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Email is not provided.",
                }
            )

        serializer = ResetPasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "Password reset link sent. Please check your email.",
                }
            )
        return Response(
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Unable to set password.",
                "response": serializer.errors,
            }
        )


class UserpasswordResetView(views.APIView):
    """
    API View for resetting a user's password.

    Handles POST requests to reset the password using a UID and token.
    """

    @custom_extend_schema(UserpasswordResetSerializer)
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
        if "password" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password is not provided.",
                }
            )
        if "password2" not in data:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Confirm password is not provided.",
                }
            )

        if not uid or not token:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "UID and token are required.",
                }
            )

        try:
            serializer = UserpasswordResetSerializer(
                data=data, context={"uid": uid, "token": token}
            )

            if serializer.is_valid(raise_exception=True):
                return Response(
                    {
                        "status_code": status.HTTP_200_OK,
                        "message": "Password reset successfully.",
                    }
                )

            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Unable to set password.",
                    "response": serializer.errors,
                }
            )

        except DjangoUnicodeDecodeError:
            return Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid UID or token.",
                }
            )


class AssignSessionView(views.APIView, CustomResponseMixin):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def patch(self, request, user_id=None, session_id=None):
        try:
            user = get_user_model().objects.get(id=user_id)

            if user.groups.filter(name="student").exists():
                obj = Student.objects.get(user=user)
                serializer_class = StudentSerializer
            elif user.groups.filter(name="instructor").exists():
                obj = Instructor.objects.get(user=user)
                serializer_class = InstructorSerializer
            else:
                return self.custom_response(
                    status.HTTP_400_BAD_REQUEST,
                    "User does not belong to a valid group (student or instructor).",
                    None,
                )

            session = Sessions.objects.get(id=session_id)

            serializer = serializer_class(
                obj, data={"session": session.id}, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.custom_response(
                    status.HTTP_200_OK,
                    "Session has been assigned to user",
                    serializer.data,
                )

            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Failed to assign session to user",
                serializer.errors,
            )

        except get_user_model().DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND, "User not found.", None
            )

        except (Student.DoesNotExist, Instructor.DoesNotExist):
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No corresponding student or instructor object found.",
                None,
            )

        except Sessions.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND, "No session object found.", None
            )

        except Exception as e:
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An unexpected error occurred: {str(e)}",
                None,
            )


class CreateStudentView(generics.CreateAPIView):
    """Create a new student in the system."""

    serializer_class = StudentSerializer

    def create(self, request, *args, **kwargs):
        user = request.data.get("user")
        session = request.data.get("session")
        batch_id = request.data.get("batch")

        try:
            batch = Batch.objects.get(batch=batch_id)
        except Batch.DoesNotExist:
            return Response(
                {"error": "Batch does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )

        if Student.objects.filter(user=user, batch=batch).exists():
            return Response(
                {"error": "This user is already registered for this batch."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student_instructor = serializer.save()
            return Response(
                {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Student successfully created",
                    "response": serializer.data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetailView(generics.RetrieveAPIView):
    """Retrieve a student/instructor by registration_id."""

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = "registration_id"


class StudentListView(CustomResponseMixin, generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_200_OK, "Students retrieved successfully", response.data
        )


class InstructorListView(CustomResponseMixin, generics.ListAPIView):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_200_OK, "Instructors retrieved successfully", response.data
        )


class InstructorCoursesViewSet(CustomResponseMixin, viewsets.ViewSet):
    """
    A viewset for retrieving all courses of an instructor based on the instructor's ID (email).
    """

    def list(self, request, *args, **kwargs):
        instructor_id = request.query_params.get("instructor_id")
        if not instructor_id:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Instructor ID is required.", None
            )

        instructor = get_object_or_404(Instructor, id=instructor_id)
        serializer = InstructorCoursesSerializer(instructor)
        return self.custom_response(
            status.HTTP_200_OK, "Courses fetched successfully.", serializer.data
        )


class AssignCoursesView(CustomResponseMixin, views.APIView):
    """Assign courses to an instructor by providing a list of course IDs."""

    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @custom_extend_schema(AssignCoursesSerializer)
    def post(self, request, instructor_id):
        serializer = AssignCoursesSerializer(data=request.data)
        if serializer.is_valid():
            course_ids = serializer.validated_data["course_ids"]
            instructor = Instructor.objects.get(id=instructor_id)
            courses = Course.objects.filter(id__in=course_ids)
            instructor.courses.set(courses)

            for course in courses:
                course.instructors.add(instructor)
                course.save()
            return self.custom_response(
                status.HTTP_200_OK, "Courses assigned successfully.", {}
            )
        return self.custom_response(
            status.HTTP_400_BAD_REQUEST, "Invalid course IDs.", serializer.errors
        )


class StudentFilterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentDetailSerializer

    def get_queryset(self):
        course_id = self.request.query_params.get("course_id", None)
        if course_id:
            return Student.objects.filter(program__courses__id=course_id)
        return Student.objects.none()


class StudentCoursesInstructorsView(views.APIView):
    def get(self, request, registration_id):
        student = get_object_or_404(Student, registration_id=registration_id)

        program = student.program
        courses = program.courses.all()

        all_instructors = Instructor.objects.filter(courses__in=courses).distinct()

        matching_instructors_emails = [
            instructor.id.email
            for instructor in all_instructors
            if instructor.session.filter(location=student.session.location).exists()
        ]

        course_names = [course.name for course in courses]
        response_data = {
            "courses": course_names,
            "instructors": matching_instructors_emails,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UsersCountAdminSectionView(views.APIView, CustomResponseMixin):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        try:
            all_users = User.objects.all()
            all_users_length = max(len(all_users) - 1, 0)
            active_users = User.objects.filter(is_active=True)
            active_users_length = max(len(active_users) - 1, 0)
            inactive_users_length = max(all_users_length - active_users_length, 0)

            student_user = User.objects.filter(groups__name="student")
            student_user_length = len(student_user)
            active_student = User.objects.filter(groups__name="student", is_active=True)
            active_student_length = len(active_student)
            inactive_student_length = max(
                student_user_length - active_student_length, 0
            )

            instructor_user = User.objects.filter(groups__name="instructor")
            instructor_user_length = len(instructor_user)
            active_instructor = User.objects.filter(
                groups__name="instructor", is_active=True
            )
            active_instructor_length = len(active_instructor)
            inactive_instructor_length = max(
                instructor_user_length - active_instructor_length, 0
            )

            data = {
                "all_users_length": all_users_length,
                "active_users_length": active_users_length,
                "inactive_users_length": inactive_users_length,
                "student_user_length": student_user_length,
                "active_student_length": active_student_length,
                "inactive_student_length": inactive_student_length,
                "instructor_user_length": instructor_user_length,
                "active_instructor_length": active_instructor_length,
                "inactive_instructor_length": inactive_instructor_length,
            }

            return self.custom_response(
                status.HTTP_200_OK, "Data fetched successfully.", data
            )

        except Exception as e:
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred: {str(e)}",
                None,
            )


class PreferredInstructorSessionView(views.APIView, CustomResponseMixin):
    """
    View to fetch sessions based on the instructor's city from the Applications table.
    """

    def get(self, request):
        instructor_id = request.query_params.get("instructor_id")

        if not instructor_id:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Instructor ID is required.",
                None,
            )
        try:
            instructor = Instructor.objects.get(id=instructor_id)
        except Instructor.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "The specified instructor does not exist.",
                None,
            )

        instructor_email = instructor.id.email

        try:
            application = Applications.objects.get(email=instructor_email)
        except Applications.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No application found for the instructor's email.",
                None,
            )

        city = application.city

        queryset = Sessions.objects.filter(location__city=city, status=1)

        if not queryset.exists():
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No sessions found for the instructor's city.",
                None,
            )
        session_data = SessionsSerializer(queryset, many=True).data
        response_data = {
            "instructor": {
                "id": instructor.id.id,
                "email": instructor_email,
            },
            "city": {
                "name": city,
            },
            "sessions": session_data,
        }

        return self.custom_response(
            status.HTTP_200_OK,
            "Instructor sessions fetched successfully.",
            response_data,
        )


class PreferredSessionView(views.APIView, CustomResponseMixin):
    """
    View to fetch sessions based on program and location filters.
    """

    def get(self, request):
        program_id = request.query_params.get("program_id")
        location_id = request.query_params.get("location_id")

        if not program_id or not location_id:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Both program_id and location_id are required.",
                None,
            )
        try:
            program = Program.objects.prefetch_related("courses").get(id=program_id)
        except Program.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "The specified program does not exist.",
                None,
            )
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "The specified location does not exist.",
                None,
            )
        courses = program.courses.all()
        print("a", courses)
        sessions = Sessions.objects.filter(
            course__in=courses, location=location, status=1
        )
        print("b", sessions)
        if not sessions.exists():
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No sessions found for the provided program and location.",
                None,
            )
        session_data = SessionsSerializer(sessions, many=True).data
        response_data = {
            "program": {
                "id": program.id,
                "name": program.name,
            },
            "location": {
                "id": location.id,
                "name": location.name,
            },
            "sessions": session_data,
        }

        return self.custom_response(
            status.HTTP_200_OK, "Sessions fetched successfully.", response_data
        )

    def post(self, request):
        user_id = request.data.get("user_id")
        session_ids = request.data.get("session_ids", [])

        # Validate if user_id and session_ids are provided
        if not user_id or not session_ids:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "user_id and session_ids are required.",
                None,
            )

        try:
            # Get the Student object based on the provided user_id
            student = Student.objects.get(user_id=user_id)

            # Use the student.user.email to fetch the application
            application = Applications.objects.get(email=student.user.email)
        except Student.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "Student does not exist for the provided user_id.",
                None,
            )

        # Fetch sessions based on provided session_ids
        sessions = Sessions.objects.filter(id__in=session_ids)

        if not sessions.exists():
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No valid sessions found for the provided session_ids.",
                None,
            )

        student_application = StudentApplicationSelection.objects.get(
            application=application
        )
        selected_location = student_application.selected_location
        created_sessions = []
        session_details = []
        date_time_slots = {}

        for session in sessions:
            if session.location != selected_location:
                return self.custom_response(
                    status.HTTP_400_BAD_REQUEST,
                    f"Selected location does not match session location for session {session.id}.",
                    None,
                )

            # Validate if the student is already assigned to this session's course
            if StudentSession.objects.filter(
                student=student, session__course=session.course, status=1
            ).exists():
                return self.custom_response(
                    status.HTTP_400_BAD_REQUEST,
                    f"Session with course {session.course.name} is already assigned to this student.",
                    None,
                )

            # Check for overlapping schedules (based on day and time)
            for schedule in session.schedules.all():
                overlapping_sessions = StudentSession.objects.filter(
                    student=student,
                    session__location=session.location,
                    session__schedules__day_of_week=schedule.day_of_week,
                    session__schedules__start_time__lt=schedule.end_time,
                    session__schedules__end_time__gt=schedule.start_time,
                    session__status=1
                ).exclude(session=session)

                # Check if overlapping sessions have overlapping date ranges
                for overlapping_session in overlapping_sessions:
                    if not (
                        session.end_date < overlapping_session.session.start_date
                        or session.start_date > overlapping_session.session.end_date
                    ):
                        return self.custom_response(
                            status.HTTP_400_BAD_REQUEST,
                            f"Session timings overlap with existing sessions for this student on {schedule.day_of_week}.",
                            None,
                        )

            # Collect start and end times for each day of the week (using schedules)
            for schedule in session.schedules.all():
                day_name = schedule.day_of_week
                if day_name not in date_time_slots:
                    date_time_slots[day_name] = []
                date_time_slots[day_name].append((schedule.start_time, schedule.end_time))

            # Create or update StudentSession entries for each session
            student_session, created = StudentSession.objects.get_or_create(
                student=student,
                session=session,
                defaults={"status": 1},
            )
            created_sessions.append(student_session)

            # Collect session details for email
            session_details.append(
                f"Course: {session.course.name}\n"
                f"Location: {session.location.name} Center\n"
                f"Timings:\n"
                + "\n".join(
                    [
                        f"{schedule.day_of_week}: {schedule.start_time} - {schedule.end_time}"
                        for schedule in session.schedules.all()
                    ]
                )
            )

        # Serialize created or updated StudentSession objects
        response_data = [
            {"session_id": sess.session.id, "student_id": sess.student.registration_id}
            for sess in created_sessions
        ]

        # Compose the email content
        email_subject = "Session Assignment Confirmation"
        email_body = (
            f"Dear {student.user.first_name} {student.user.last_name},\n\n"
            f"You have been successfully assigned to the following sessions as per your program:\n\n"
            + "\n\n".join(session_details)
            + "\n\nPlease make sure to attend these sessions on time.\n"
            f"Login to the portal from the link below, and start your learning journey.\n"
            f"https://lms-phi-two.vercel.app/auth/login"
        )

        email_data = {
            "email_subject": email_subject,
            "body": email_body,
            "to_email": student.user.email,
        }

        # Send email (using the existing send_email function or Django's default send_mail)
        send_email(email_data)

        return self.custom_response(
            status.HTTP_200_OK,
            "Sessions assigned successfully and email sent.",
            response_data,
        )

class UserSessionsView(views.APIView, CustomResponseMixin):
    """View to get all sessions assigned to a specific user."""

    def get(self, request, user_id):
        # Determine whether the user is a student or instructor
        group_name = request.query_params.get("group_name")
        course_id = request.query_params.get("course_id")

        if group_name not in ["student", "instructor"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid group_name. Choices are 'student' and 'instructor'.",
                None,
            )

        if group_name == "student":
            try:
                # Fetch the student based on the user_id
                student = Student.objects.get(user__id=user_id)
            except Student.DoesNotExist:
                return self.custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "Student with the given user_id does not exist.",
                    None,
                )

            # Fetch all sessions assigned to this student
            user_sessions = StudentSession.objects.filter(student=student, status=1)

        elif group_name == "instructor":
            try:
                # Fetch the instructor based on the user_id
                instructor = Instructor.objects.get(user__id=user_id)
            except Instructor.DoesNotExist:
                return self.custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "Instructor with the given user_id does not exist.",
                    None,
                )

            # If course_id is provided, filter instructor sessions by course
            if course_id:
                user_sessions = InstructorSession.objects.filter(
                    instructor=instructor,
                    session__course__id=course_id,  # Filter sessions based on course_id
                    status=1,
                )
            else:
                # Fetch all sessions assigned to this instructor
                user_sessions = InstructorSession.objects.filter(
                    instructor=instructor, status=1
                )

        if not user_sessions.exists():
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No sessions found for this user.",
                None,
            )

        # Serialize the session data with all relevant fields
        session_data = []
        for user_session in user_sessions:
            session = user_session.session  # Access the related session object
            # Fetch schedules for the session
            session_schedules = session.schedules.all()

            # Gather schedule info for each session (day-wise start and end times)
            schedule_info = [
                {
                    "day_of_week": schedule.day_of_week,
                    "start_time": schedule.start_time.strftime("%H:%M:%S"),
                    "end_time": schedule.end_time.strftime("%H:%M:%S"),
                }
                for schedule in session_schedules
            ]

            session_info = {
                "session_id": session.id,
                "status": user_session.status,  # Session-specific status
                "course": session.course.name if session.course else None,
                "location": session.location.name if session.location else None,
                "schedules": schedule_info,  # Include schedules in the response
                "no_of_students": session.no_of_students,
            }
            session_data.append(session_info)

        return self.custom_response(
            status.HTTP_200_OK,
            "Sessions fetched successfully.",
            session_data,
        )

    def delete(self, request, *args, user_id, **kwargs):
        session_id = request.query_params.get("pk", None)
        group_name = request.query_params.get("group_name")

        if not group_name:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "group_name query param is required.",
                None,
            )

        if group_name not in ["student", "instructor"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid group_name. Choices are 'student' and 'instructor'.",
                None,
            )

        # Get the session instance
        instance = get_object_or_404(Sessions, id=session_id)

        if group_name == "student":
            try:
                # Get the student session based on the user_id and session_id
                student = Student.objects.get(user__id=user_id)
                student_session = StudentSession.objects.get(
                    student=student, session=instance
                )
            except (Student.DoesNotExist, StudentSession.DoesNotExist):
                return self.custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "Student or session not found for the given user.",
                    None,
                )
            # Update the status to 2 (soft delete)
            student_session.status = 2
            student_session.save()

        elif group_name == "instructor":
            try:
                # Get the instructor session based on the user_id and session_id
                instructor = Instructor.objects.get(user__id=user_id)
                instructor_session = InstructorSession.objects.get(
                    instructor=instructor, session=instance
                )
            except (Instructor.DoesNotExist, InstructorSession.DoesNotExist):
                return self.custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "Instructor or session not found for the given user.",
                    None,
                )
            # Update the status to 2 (soft delete)
            instructor_session.status = 2
            instructor_session.save()

        return Response(
            {
                "status_code": status.HTTP_204_NO_CONTENT,
                "message": f"Session deleted successfully for {group_name}.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class InstructorSessionsView(views.APIView, CustomResponseMixin):
    """
    View to assign sessions to an instructor.
    """

    def post(self, request):
        user_id = request.data.get("user_id")
        session_ids = request.data.get("session_ids", [])

        # Validate if user_id and session_ids are provided
        if not user_id or not session_ids:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "user_id and session_ids are required.",
                None,
            )
        try:
            # Correctly fetching the instructor using the ID field
            instructor = Instructor.objects.get(id__id=user_id)
            print("jbcec",instructor)
        except Instructor.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "Instructor does not exist for the provided user_id.",
                None,
            )
        # Fetch sessions based on provided session_ids
        sessions = Sessions.objects.filter(id__in=session_ids)
        if not sessions.exists():
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No valid sessions found for the provided session_ids.",
                None,
            )

        created_sessions = []
        session_details = []
        date_time_slots = {}

        for session in sessions:
            course = session.course

            # Check if the session is already assigned to this instructor
            instructor_session = InstructorSession.objects.filter(
                instructor=instructor,
                session=session,
            ).first()

            if instructor_session:
                # Check if the session is already assigned to another instructor with status 1
                if InstructorSession.objects.filter(
                    session=session, status=1
                ).exclude(instructor=instructor).exists():
                    return self.custom_response(
                        status.HTTP_400_BAD_REQUEST,
                        f"Session with course {session.course.name} is already assigned to another instructor.",
                        None,
                    )

                # If session is already assigned to this instructor but inactive (status=2), activate it
                if instructor_session.status == 2:
                    instructor_session.status = 1
                    instructor_session.save()
                    created_sessions.append(instructor_session)
                    continue

                # Skip this session if it's already assigned with the correct status
                continue

            # Check for schedule conflicts with the instructor's existing sessions
            session_schedules = session.schedules.all()

            for schedule in session_schedules:
                # Check for overlapping schedules
                overlapping_sessions = InstructorSession.objects.filter(
                    instructor=instructor,
                    session__schedules__day_of_week=schedule.day_of_week,
                    # session__start_date__lte=session.end_date,
                    # session__end_date__gte=session.start_date,
                    session__schedules__start_time__lt=schedule.end_time,
                    session__schedules__end_time__gt=schedule.start_time,
                ).exclude(session=session)

                if overlapping_sessions.exists():
                    return self.custom_response(
                        status.HTTP_400_BAD_REQUEST,
                        f"Session timings for {course.name} overlap with existing sessions for this instructor.",
                        None,
                    )

            # Create or update InstructorSession entries for each session
            instructor_session, created = InstructorSession.objects.get_or_create(
                instructor=instructor,
                session=session,
                defaults={
                    "status": 1,  # Default status
                },
            )
            created_sessions.append(instructor_session)

            if session.course:
                session.course.instructors.add(instructor)
            print("ecneicneo",session_schedules)
            # Collect session details for email
            session_details.append(
                f"Course: {course.name}\n"
                f"Location: {session.location.name} Center\n"
                f"Timings: {', '.join([f'{sch.start_time} - {sch.end_time} on {sch.day_of_week}' for sch in session_schedules])}\n"
            )

        # Serialize created or updated InstructorSession objects with detailed session data
        response_data = [
            {
                "instructor_email": sess.instructor.id.email,
                "session": {
                    "session_id": sess.session.id,
                    "course_name": sess.session.course.name,
                    "status": sess.status,
                },
            }
            for sess in created_sessions
        ]

        # Compose the email content
        email_subject = "Session Assignment Notification"
        email_body = (
            f"Dear {instructor.id.first_name} {instructor.id.last_name},\n\n"
            f"You have been assigned to the following sessions:\n\n"
            + "\n\n".join(session_details)
            + "\n\nPlease review your schedule and be prepared for your upcoming sessions.\n"
            f"Login to the portal from the link below to view details and manage your sessions.\n"
            f"https://lms-phi-two.vercel.app/auth/login"
        )

        # Email configuration
        email_data = {
            "email_subject": email_subject,
            "body": email_body,
            "to_email": instructor.id.email,
        }

        # Send email
        send_email(email_data)

        return self.custom_response(
            status.HTTP_200_OK,
            "Sessions assigned successfully and email sent.",
            response_data,
        )



class ApplicationUserView(views.APIView, CustomResponseMixin):
    """View to fetch applications and user details based on group (student or instructor)."""

    def get(self, request, filteration_id=None):
        if filteration_id is None:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "filteration_id is not provided.", None
            )

        group_name = request.query_params.get("group_name")

        if group_name not in ["student", "instructor"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid group_name. Choices are 'student' and 'instructor'.",
                None,
            )

        try:
            response_data = {"count": 0, "data": []}

            if group_name == "student":
                student_selection = StudentApplicationSelection.objects.filter(
                    selected_program_id=filteration_id
                ).select_related("application")

                if not student_selection.exists():
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        "No student applications found for the provided program ID.",
                        None,
                    )

                for selection in student_selection:
                    application = selection.application

                    # Ensure both the application and user exist
                    try:
                        user = User.objects.get(email=application.email)
                    except User.DoesNotExist:
                        user = None

                    # Only add the data if both application and user are valid
                    if user:
                        response_data["data"].append(
                            {
                                "application": ApplicationSerializer(application).data,
                                "user": UserSerializer(user).data,
                            }
                        )

                # Update the count based on the filtered data
                response_data["count"] = len(response_data["data"])

            elif group_name == "instructor":
                instructor_selection = (
                    InstructorApplicationSelection.objects.filter(
                        selected_skills__id=filteration_id
                    )
                    .select_related("application")
                    .distinct()
                )

                if not instructor_selection.exists():
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        "No instructor applications found for the provided skills ID.",
                        None,
                    )

                for selection in instructor_selection:
                    application = selection.application

                    # Ensure both the application and user exist
                    try:
                        user = User.objects.get(email=application.email)
                    except User.DoesNotExist:
                        user = None

                    # Only add the data if both application and user are valid
                    if user:
                        response_data["data"].append(
                            {
                                "application": ApplicationSerializer(application).data,
                                "user": UserSerializer(user).data,
                            }
                        )

                # Update the count based on the filtered data
                response_data["count"] = len(response_data["data"])

            return self.custom_response(
                status.HTTP_200_OK,
                "Applications fetched successfully.",
                response_data,
            )

        except Exception as e:
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An unexpected error occurred: {str(e)}",
                None,
            )


class UserDetailsView(views.APIView, CustomResponseMixin):
    """View to fetch program, location, skills, and other details based on user ID."""

    def get(self, request, user_id=None):
        if user_id is None:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "user_id is not provided.", None
            )

        group_name = request.query_params.get("group_name")

        if group_name not in ["student", "instructor"]:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid group_name. Choices are 'student' and 'instructor'.",
                None,
            )

        try:
            response_data = {}

            if group_name == "student":
                # Retrieve the student object using user_id
                try:
                    student = Student.objects.get(user_id=user_id)
                    user = student.user  # Get the associated User object
                except Student.DoesNotExist:
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        "Student does not exist for the provided user ID.",
                        None,
                    )

                # Fetch the application using the user's email
                try:
                    application = Applications.objects.get(email=user.email)
                except Applications.DoesNotExist:
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        f"No application found for user email {user.email}.",
                        None,
                    )

                # Retrieve program and location details from StudentApplicationSelection
                student_selection = StudentApplicationSelection.objects.filter(
                    application=application
                )

                if not student_selection.exists():
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        "No related student application selections found.",
                        None,
                    )

                response_data["programs"] = [
                    ProgramSerializer(selection.selected_program).data
                    for selection in student_selection
                ]
                response_data["locations"] = [
                    LocationSerializer(selection.selected_location).data
                    for selection in student_selection
                ]

            elif group_name == "instructor":
                # Retrieve the instructor object using user_id
                try:
                    instructor = Instructor.objects.get(id__id=user_id)
                    user = instructor.id  # Get the associated User object
                except Instructor.DoesNotExist:
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        "Instructor does not exist for the provided user ID.",
                        None,
                    )

                # Fetch the application using the user's email
                try:
                    application = Applications.objects.get(email=user.email)
                except Applications.DoesNotExist:
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        f"No application found for user email {user.email}.",
                        None,
                    )

                # Retrieve skills and location details from InstructorApplicationSelection
                instructor_selection = InstructorApplicationSelection.objects.filter(
                    application=application
                )

                if not instructor_selection.exists():
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        "No related instructor application selections found.",
                        None,
                    )

                # Gather skills and locations from the selections
                response_data["skills"] = TechSkillSerializer(
                    [
                        skill
                        for selection in instructor_selection
                        for skill in selection.selected_skills.all()
                    ],
                    many=True,
                ).data
                response_data["locations"] = LocationSerializer(
                    [
                        location
                        for selection in instructor_selection
                        for location in selection.selected_locations.all()
                    ],
                    many=True,
                ).data

            return self.custom_response(
                status.HTTP_200_OK,
                "Details fetched successfully.",
                response_data,
            )

        except Exception as e:
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An unexpected error occurred: {str(e)}",
                None,
            )


class BatchStudentView(views.APIView, CustomResponseMixin):

    def get(self, request):
        batch_name = request.GET.get("batch_name")
        if not batch_name:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST, "Batch name parameter is missing.", "None"
            )
        try:
            students = Student.objects.filter(registration_id__icontains=batch_name)
            if not students.exists():
                return self.custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "No students found for the given batch name.",
                    "None",
                )
            response_data = [
                {
                    "registration_id": student.registration_id,
                    "name": f"{student.user.first_name} {student.user.last_name}",
                }
                for student in students
            ]
            return self.custom_response(
                status.HTTP_200_OK, "Students fetched successfully.", response_data
            )
        except Exception as e:
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred: {str(e)}",
                "None",
            )
