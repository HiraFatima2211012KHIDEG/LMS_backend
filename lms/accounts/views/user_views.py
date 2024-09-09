from rest_framework import views, status, generics, permissions
from rest_framework.response import Response
from ..serializers.user_serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema
from ..serializers.user_serializers import (
    UserSerializer,
    StudentSerializer,
    AdminUserSerializer,
)
from ..models.user_models import Student
import constants
from utils.custom import CustomResponseMixin, custom_extend_schema
from course.models.models import Course
from ..serializers.location_serializers import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from ..serializers.application_serializers import *
from course.serializers import *


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        # Save the user and return the created user instance
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


class UserLoginView(views.APIView, CustomResponseMixin):
    """
    View to handle user login and generate authentication tokens.
    """

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
                print("user_group", user_group)
                permission = self.get_group_permissions(user_group.id)
                user_profile = UserProfileSerializer(user, context={'user' : user})
                user_object_id = User.objects.get(email= user.email).id
                print("user_object", user_object_id)
                user_serializer = None
                session_data = None  # Initialize session_data as None
                if user_group.name == "student":
                    student = Student.objects.get(user=user.id)
                    user_serializer = StudentSerializer(student)
                    try:
                        student_session = StudentSession.objects.get(student=student)
                        # Serialize session details if needed
                        if student_session:
                            session_data = SessionsSerializer(student_session.session).data
                        else:
                            session_data = None
                    except StudentSession.DoesNotExist:
                        return self.custom_response(
                                status.HTTP_404_NOT_FOUND,
                                "No student session found.",
                                None,
                        )  # Handle case when no session is assigned

                elif user_group.name == "instructor":
                    print("inside instuctor")
                    print(user_object_id)
                    instructor = Instructor.objects.get(id_id=user_object_id)
                    print("instructor", instructor)
                    user_serializer = InstructorSerializer(instructor)
                    print("user_serializer for instructor", user_serializer.data)
                    try:
                        # Use .filter() to get all sessions for the instructor
                        print("inside instructor session")
                        instructor_sessions = InstructorSession.objects.filter(instructor=instructor)
                        print("instructor session", instructor_sessions)

                        # Serialize all sessions if needed
                        if instructor_sessions.exists():
                            print("inside if")
                            # Serialize all sessions as a list
                            session_data = SessionsSerializer(
                                [session.session for session in instructor_sessions], many=True
                            ).data
                            print("if working")
                        else:
                            session_data = None
                    except InstructorSession.DoesNotExist:
                        return self.custom_response(
                            status.HTTP_404_NOT_FOUND,
                            "No instructor session found.",
                            None,
                        )


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
                            "session": session_data if session_data else None,
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

    # class UserLoginView(views.APIView):
    #     """
    #     View to handle user login and generate authentication tokens.
    #     """
    #     @extend_schema(
    #         request=UserLoginSerializer,
    #         responses={
    #             200: "Login Successful.",
    #             400: "Bad Request.",
    #             401: "Unauthorized.",
    #         },
    #     )
    #     def post(self, request):
    #         """
    #         Handle POST requests for user login.
    #         This method processes the login request by validating the provided credentials.
    #         If valid, it authenticates the user and generates authentication tokens.
    #         Args:
    #             request (Request): The HTTP request object containing the login data.
    #         Returns:
    #             Response: A Response object with authentication tokens if successful,
    #                       or error details if validation fails.
    #         """
    #         data = request.data
    #         if "email" not in data:
    #             return Response(
    #                 {
    #                     "status_code": status.HTTP_400_BAD_REQUEST,
    #                     "message": "Email is not provided.",
    #                 }
    #             )
    #         if "password" not in data:
    #             return Response(
    #                 {
    #                     "status_code": status.HTTP_400_BAD_REQUEST,
    #                     "message": "Password is not provided.",
    #                 }
    #             )
    #         data["email"] = data.get("email", "").lower()
    #         serializer = UserLoginSerializer(data=data)
    #         if serializer.is_valid(raise_exception=True):
    #             user = authenticate(
    #                 email=serializer.validated_data["email"],
    #                 password=serializer.validated_data["password"],
    #             )
    #             if user is not None:
    #                 tokens = self.get_tokens_for_user(user)
    #                 user_group = Group.objects.get(user=user.id)
    #                 permission = self.get_group_permissions(user_group.id)
    #                 user_profile = UserProfileSerializer(user)
    #                 return Response(
    #                     {
    #                         "status_code": status.HTTP_200_OK,
    #                         "message": "Login Successful.",
    #                         "response": {
    #                             "token": tokens,
    #                             "Group": user_group.name,
    #                             "user": user_profile.data,
    #                             "permissions": permission,

    #                         },
    #                     }
    #                 )
    #             else:
    #                 return Response(
    #                     {
    #                         "status_code": status.HTTP_401_UNAUTHORIZED,
    #                         "message": "Invalid credentials.",
    #                     },
    #                 )
    #         return Response(
    #             {
    #                 "status_code": status.HTTP_400_BAD_REQUEST,
    #                 "message": "Unable to login.",
    #                 "response": serializer.errors,
    #             }
    #         )
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
            # Retrieve the user
            user = get_user_model().objects.get(id=user_id)

            # Determine the group (student or instructor)
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

            # Retrieve the session
            session = Sessions.objects.get(id=session_id)

            # Serialize the object with the session_id
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
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        try:
            # Fetch all users
            all_users = User.objects.all()
            all_users_length = max(len(all_users) - 1, 0)  # 1 superadmin user is excluded

            # Fetch active users
            active_users = User.objects.filter(is_active=True)
            active_users_length = max(len(active_users) -1, 0) 
            inactive_users_length = max(all_users_length - active_users_length, 0)

            # Fetch student users
            student_user = User.objects.filter(groups__name='student')
            student_user_length = len(student_user)
            active_student = User.objects.filter(groups__name='student', is_active=True)
            active_student_length = len(active_student)
            inactive_student_length = max(student_user_length - active_student_length, 0)

            # Fetch instructor users
            instructor_user = User.objects.filter(groups__name='instructor')
            instructor_user_length = len(instructor_user)
            active_instructor = User.objects.filter(groups__name='instructor', is_active=True)
            active_instructor_length = len(active_instructor)
            inactive_instructor_length = max(instructor_user_length - active_instructor_length, 0)

            # Data dictionary with all counts
            data = {
                'all_users_length': all_users_length,
                'active_users_length': active_users_length,
                'inactive_users_length': inactive_users_length,
                'student_user_length': student_user_length,
                'active_student_length': active_student_length,
                'inactive_student_length': inactive_student_length,
                'instructor_user_length': instructor_user_length,
                'active_instructor_length': active_instructor_length,
                'inactive_instructor_length': inactive_instructor_length,
            }

            # Returning the successful response with data
            return self.custom_response(
                status.HTTP_200_OK,
                "Data fetched successfully.",
                data
            )

        except Exception as e:
            # Handle unexpected errors
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An error occurred: {str(e)}",
                None
            )



class UserProcessView(views.APIView, CustomResponseMixin):
    """View to handle users based on their group (student or instructor)."""

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
            if group_name == "student":
                # Filter StudentApplicationSelection based on the selected program
                student_selection = StudentApplicationSelection.objects.filter(
                    selected_program_id=filteration_id
                ).select_related('application')

                if not student_selection.exists():
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        "No student applications found for the provided program ID.",
                        None,
                    )

                response_data = []
                for selection in student_selection:
                    application = selection.application

                    try:
                        user = User.objects.get(email=application.email)
                    except User.DoesNotExist:
                        return self.custom_response(
                            status.HTTP_404_NOT_FOUND,
                            f"User with email {application.email} does not exist.",
                            None,
                        )

                    response_data.append({
                        "application": ApplicationSerializer(application).data,
                        "user": UserSerializer(user).data,
                        "program": ProgramSerializer(selection.selected_program).data,
                        "location": LocationSerializer(selection.selected_location).data,
                    })

                return self.custom_response(
                    status.HTTP_200_OK,
                    "Student applications fetched successfully.",
                    response_data,
                )

            elif group_name == "instructor":
                # Filter InstructorApplicationSelection based on selected skills
                instructor_selection = InstructorApplicationSelection.objects.filter(
                    selected_skills__id=filteration_id
                ).select_related('application').distinct()

                if not instructor_selection.exists():
                    return self.custom_response(
                        status.HTTP_404_NOT_FOUND,
                        "No instructor applications found for the provided skills ID.",
                        None,
                    )

                response_data = []
                for selection in instructor_selection:
                    application = selection.application

                    try:
                        user = User.objects.get(email=application.email)
                    except User.DoesNotExist:
                        return self.custom_response(
                            status.HTTP_404_NOT_FOUND,
                            f"User with email {application.email} does not exist.",
                            None,
                        )

                    selected_skills = selection.selected_skills.all()
                    selected_locations = selection.selected_locations.all()

                    # Check if selected_skills and selected_locations exist
                    if not selected_skills.exists():
                        return self.custom_response(
                            status.HTTP_404_NOT_FOUND,
                            "No skills found for the instructor application.",
                            None,
                        )

                    if not selected_locations.exists():
                        return self.custom_response(
                            status.HTTP_404_NOT_FOUND,
                            "No locations found for the instructor application.",
                            None,
                        )

                    response_data.append({
                        "application": ApplicationSerializer(application).data,
                        "user": UserSerializer(user).data,
                        "skills": TechSkillSerializer(selected_skills, many=True).data,
                        "locations": LocationSerializer(selected_locations, many=True).data,
                    })

                return self.custom_response(
                    status.HTTP_200_OK,
                    "Instructor applications fetched successfully.",
                    response_data,
                )

        except Exception as e:
            # Catch any unexpected exceptions and log them if necessary
            return self.custom_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"An unexpected error occurred: {str(e)}",
                None,
            )


class PreferredSessionView(views.APIView, CustomResponseMixin):
    """
    View to fetch sessions based on program and location filters.
    """

    def get(self, request):
        program_id = request.query_params.get("program_id")
        location_id = request.query_params.get("location_id")

        # Check if both program_id and location_id are provided
        if not program_id or not location_id:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Both program_id and location_id are required.",
                None,
            )

        try:
            # Check if the specified program exists
            program = Program.objects.prefetch_related('courses').get(id=program_id)
        except Program.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "The specified program does not exist.",
                None,
            )

        try:
            # Check if the specified location exists
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "The specified location does not exist.",
                None,
            )

        # Get all courses associated with the specified program
        courses = program.courses.all()
        print('a', courses)

        # Fetch sessions based on the courses and the specified location
        sessions = Sessions.objects.filter(course__in=courses, location=location)
        print('b', sessions)

        # Check if any sessions match the criteria
        if not sessions.exists():
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No sessions found for the provided program and location.",
                None,
            )

        # Serialize the session data
        session_data = SessionsSerializer(sessions, many=True).data

        # Prepare the response data with location and program details
        response_data = {
            'program': {
                'id': program.id,
                'name': program.name,  # Adjust according to your Program model fields
                # Add other Program fields if needed
            },
            'location': {
                'id': location.id,
                'name': location.name,  # Adjust according to your Location model fields
                # Add other Location fields if needed
            },
            'sessions': session_data
        }

        return self.custom_response(
            status.HTTP_200_OK,
            "Sessions fetched successfully.",
            response_data
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

        created_sessions = []

        for session in sessions:
            # Get the associated course for the session
            course = session.course

            # Create or update StudentSession entries for each session
            student_session, created = StudentSession.objects.get_or_create(
                student=student,
                session=session,
                defaults={
                    'status': 1,  # Default status or modify based on your needs
                    'start_date': course.start_date if course.start_date else None,
                    'end_date': course.end_date if course.end_date else None,
                }
            )
            created_sessions.append(student_session)

        # Serialize created or updated StudentSession objects
        # You can use a serializer if needed for better response structure
        response_data = [{"session_id": sess.session.id, "student_id": sess.student.registration_id} for sess in created_sessions]

        return self.custom_response(
            status.HTTP_200_OK,
            "Sessions assigned successfully.",
            response_data
        )


class UserSessionsView(views.APIView, CustomResponseMixin):
    """View to get all sessions assigned to a specific user."""

    def get(self, request, user_id):
        # Determine whether the user is a student or instructor
        group_name = request.query_params.get("group_name")

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
                    None
                )

            # Fetch all sessions assigned to this student
            user_sessions = StudentSession.objects.filter(student=student)

        elif group_name == "instructor":
            try:
                # Fetch the instructor based on the user_id
                instructor = Instructor.objects.get(id__id=user_id)
            except Instructor.DoesNotExist:
                return self.custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "Instructor with the given user_id does not exist.",
                    None
                )

            # Fetch all sessions assigned to this instructor
            user_sessions = InstructorSession.objects.filter(instructor=instructor)

        else:
            return self.custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid user_type provided. Use 'student' or 'instructor'.",
                None
            )

        if not user_sessions.exists():
            return self.custom_response(
                status.HTTP_404_NOT_FOUND,
                "No sessions found for this user.",
                None
            )

        # Serialize the session data
        session_data = []
        for session in user_sessions:
            session_info = {
                "session_id": session.session.id,
                "status": session.status,
                "start_date": session.start_date,
                "end_date": session.end_date,
                # "batch": session.session.batch.name if session.session.batch else None, 
                "course": session.session.course.name if session.session.course else None
            }
            session_data.append(session_info)

        return self.custom_response(
            status.HTTP_200_OK,
            "Sessions fetched successfully.",
            session_data
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
            # Get the Instructor object based on the provided user_id
            instructor = Instructor.objects.get(id__id=user_id)  # Adjusted to use the email field
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

        for session in sessions:
            course = session.course
            # Create or update InstructorSession entries for each session
            instructor_session, created = InstructorSession.objects.get_or_create(
                instructor=instructor,
                session=session,
                defaults={
                    'status': 1,  # Default status or modify based on your needs
                    'start_date': course.start_date if course.start_date else None,
                    'end_date': course.end_date if course.end_date else None,
                }
            )
            created_sessions.append(instructor_session)

        # Serialize created or updated InstructorSession objects with detailed session data
        response_data = [{
            "instructor_email": sess.instructor.id.email,  # Instructor's email
            "session": {
                "session_id": sess.session.id,
                # "session_name": sess.session.name,  # Replace with actual field name if different
                "course_name": sess.session.course.name,  # Accessing course details
                "start_date": sess.start_date,
                "end_date": sess.end_date,
                "status": sess.status,
            }
        } for sess in created_sessions]

        return self.custom_response(
            status.HTTP_200_OK,
            "Sessions assigned successfully.",
            response_data
        )

