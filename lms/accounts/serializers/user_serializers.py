"""
Serializers for the User API View.
"""

from django.contrib.auth import (
    get_user_model,
)
from django.utils.translation import gettext as _
from rest_framework import serializers
from accounts.models import *
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.hashers import check_password
import re
from accounts.utils import send_email
from ..models.user_models import *
from course.models.models import Course
from django.contrib.auth.models import Group

# from accounts.utils import send_email


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "contact",
            "city",
        ]
        extra_kwargs = {"password": {"write_only": True, "max_length": 50}}

    def validate(self, attrs):
        password = attrs.get("password")
        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        if " " in password:
            raise serializers.ValidationError("Password cannot contain spaces.")

        if not re.match(
            r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&^#(){}[\]=+/\\|_\-<>])[A-Za-z\d@$!%*?&^#(){}[\]=+/\\|_\-<>]+$",
            password,
        ):
            raise serializers.ValidationError(
                "Password must contain letters, numbers, and special characters."
            )

        return super().validate(attrs)

    def create(self, validated_data):
        """Create and Return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """update an return a user."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(validated_data.get(password))
            user.save()
        return user

    def perform_create(self, serializer):
        # Save the user and return the created user instance
        return serializer.save()

class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return User.objects.create_admin(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)


# class UserLoginSerializer(serializers.ModelSerializer):
#     """Serializer for user login"""

#     class Meta:
#         model = get_user_model()
#         fields = ['email', 'password']
#         extra_kwargs = {'password': {'write_only': True, 'min_length':  5}}

# email = serializers.EmailField()
# password = serializers.CharField(style = {'input_type' : 'password'}, write_only = True)


# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'first_name', 'last_name', 'contact', 'city']

class UserProfileSerializer(serializers.ModelSerializer):
    registration_id = serializers.CharField(
        source="student.registration_id", read_only=True
    )
    email = serializers.EmailField(read_only=True)
    program = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "contact",
            "city",
            "registration_id",
            "email",
            "program",
            "course",
        ]

    def __init__(self, *args, **kwargs):
        super(UserProfileSerializer, self).__init__(*args, **kwargs)
        user = self.context.get("user")

        if user and user.groups.filter(name="student").exists():
            self.fields.pop("course")
        elif user and user.groups.filter(name="instructor").exists():
            self.fields.pop("program")

    # def get_program(self, obj):
    #     try:
    #         application = Applications.objects.get(email=obj.email)
    #         student_program = StudentApplicationSelection.objects.get(
    #             application=application
    #         )
    #         return {
    #             "id": student_program.selected_program.id,
    #             "name": student_program.selected_program.name,
    #         }
    #     except (Applications.DoesNotExist, StudentApplicationSelection.DoesNotExist):
    #         return None

    # def get_course(self, obj):
    #     try:
    #         application = Applications.objects.get(email=obj.email)
    #         instructor = Instructor.objects.get(user=obj)
    #         courses = instructor.courses.all()
    #         return [{"id": course.id, "name": course.name} for course in courses]
    #     except (Applications.DoesNotExist, Instructor.DoesNotExist):
    #         return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "contact"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "contact": {"required": False},
        }

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    password = serializers.CharField(
        max_length=50, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=50, style={"input_type": "password"}, write_only=True
    )
    def validate(self, data):
        """
        Validate that new_password and password2 match, and that new_password meets complexity requirements.
        """
        password = data.get("password")
        password2 = data.get("password2")
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError(
                "Password and confirm password are not the same."
            )
        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if " " in password:
            raise serializers.ValidationError("Password cannot contain spaces.")
        if not re.match(
            r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&^#(){}[\]=+/\\|_\-<>])[A-Za-z\d@$!%*?&^#(){}[\]=+/\\|_\-<>]+$",
            password,
        ):
            raise serializers.ValidationError(
                "Password must contain letters, numbers, and special characters."
            )
        if user and check_password(password, user.password):
            raise serializers.ValidationError(
                "New password cannot be the same as the old one."
            )
        return data
    def validate_old_password(self, old_password):
        user = self.context.get("user")
        if not check_password(old_password, user.password):
            raise serializers.ValidationError("Old password is incorrect.")
        return old_password
    def save(self):
        user = self.context.get("user")
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()

class SetPasswordSerializer(serializers.Serializer):
    """
    Serializer for setting a new password without requiring the old password.
    """
    password = serializers.CharField(
        max_length=50, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=50, style={"input_type": "password"}, write_only=True
    )
    def validate_password(self, value):
        """
        Validate that the password meets complexity requirements.
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password should be at least 8 characters long."
            )
        if " " in value:
            raise serializers.ValidationError("Password cannot contain spaces.")
        if not re.match(
            r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&^#(){}[\]=+/\\|_\-<>])[A-Za-z\d@$!%*?&^#(){}[\]=+/\\|_\-<>]+$",
            value,
        ):
            raise serializers.ValidationError(
                "Password should contain letters, numbers, and special characters."
            )
        return value
    def validate(self, data):
        """
        Validate that the password and password2 fields match, and that the new password is not the same as the old password.
        """
        password = data.get("password")
        password2 = data.get("password2")
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError(
                "Password and confirm password are not the same."
            )
        return data
    def save(self):
        """
        Set the new password for the user and save the user instance.
        """
        user = self.context.get("user")
        new_password = self.validated_data["password"]
        user.set_password(new_password)
        user.save()


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for requesting a password reset email."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Check if the email exists in the system and generate a password reset link.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("You are not a registered user")

        user = User.objects.get(email=value)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        link = f"https://lms-phi-two.vercel.app/auth/set-password/{uid}/{token}"
        print("Password reset link:", link)

        # Email sending logic can be included here or in a separate function/task
        # Example:
        body = f"Hey {user.first_name} {user.last_name},\nPlease click the following link to reset your password. {link}\nThe link will expire in 10 minutes."
        data = {
             "email_subject": "Reset Password",
             "body": body,
             "to_email": user.email,
         }
        send_email(data)

        return value

class UserpasswordResetSerializer(serializers.Serializer):
    """
    Serializer for resetting the user's password.
    """
    password = serializers.CharField(
        max_length=50, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=50, style={"input_type": "password"}, write_only=True
    )
    class Meta:
        fields = ["password", "password2"]
    def validate_password(self, value):
        """
        Validate the password for required complexity.
        Args:
            value (str): The new password to validate.
        Returns:
            str: The validated password.
        Raises:
            serializers.ValidationError: If the password does not meet complexity requirements.
        """
        # Check if password length is at least 8 characters
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password should be at least 8 characters long."
            )
        # Check if password contains alphabets, numeric, and special characters
        if " " in value:
            raise serializers.ValidationError("Password cannot contain spaces.")
        if not re.match(
            r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&^#(){}[\]=+/\\|_\-<>])[A-Za-z\d@$!%*?&^#(){}[\]=+/\\|_\-<>]+$",
            value,
        ):
            raise serializers.ValidationError(
                "Password should contain letters, numbers, and special characters."
            )
        return value
    def validate(self, data):
        """
        Validate that the passwords match and the token is valid.
        Args:
            data (dict): The input data containing passwords and reset token details.
        Returns:
            dict: The validated data.
        Raises:
            serializers.ValidationError: If validation fails for any reason.
        """
        try:
            password = data.get("password")
            password2 = data.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")
            if password != password2:
                raise serializers.ValidationError(
                    "Password and confirm password are not the same."
                )
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not valid or expired.")
            if user and check_password(password, user.password):
                raise serializers.ValidationError(
                    "New password cannot be the same as the old one."
                )
            user.set_password(password)
            user.save()
            return data
        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError("Token is not valid or expired.")


class StudentSerializer(serializers.ModelSerializer):
    session_details = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ["registration_id", "user", "session","session_details"]
    def get_session_details(self, obj):
        return obj.get_session_details()

class InstructorSerializer(serializers.ModelSerializer):
    # session_details = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = "__all__"
    # def get_session_details(self, obj):
    #     return obj.get_session_details()

class AssignCoursesSerializer(serializers.Serializer):
    course_ids = serializers.ListField(child=serializers.IntegerField())

    def validate_course_ids(self, value):
        # Ensure all course IDs are valid
        if not Course.objects.filter(id__in=value).exists():
            raise serializers.ValidationError("Some course IDs are invalid.")
        return value

class InstructorSessionSerializer(serializers.ModelSerializer):
    # instructor_email = serializers.SerializerMethodField()

    class Meta:
        model = InstructorSession
        fields = ['session', 'instructor' ,'status', 'start_date', 'end_date']

    # def get_instructor_email(self, obj):
    #     # Ensure obj.instructor exists and has an email
    #     return obj.instructor.id.email if obj.instructor and obj.instructor.id else None