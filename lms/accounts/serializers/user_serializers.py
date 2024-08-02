"""
Serializers for the User API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from rest_framework import serializers
from accounts.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.hashers import check_password
import re


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name','password', 'contact', 'city']
        extra_kwargs = {'password': {'write_only': True, 'min_length':  5}}

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        """Create and Return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """update an return a user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


# class AuthTokenSerializer(serializers.Serializer):
#     """Serializer for the user auth token."""
#     email = serializers.EmailField()
#     password = serializers.CharField(
#         style = {'input_type': 'password'},
#         trim_whitespace = False
#     )

#     def validate(self, attrs):
#         """Validate and Authenticate the user."""
#         email = attrs.get('email')
#         password = attrs.get('password')
#         user = authenticate(
#             username = email,
#             password = password
#         )
#         if not user:
#             msg = _("Unable to authenticate user with provided credentials.")
#             raise serializers.ValidationError(msg, code='authorization')
#         attrs['user'] = user
#         return attrs


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    email = serializers.EmailField()
    password = serializers.CharField(style = {'input_type' : 'password'}, trim_whitespace = False)


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name','contact', 'city']
            
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    password2 = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        """
        Validate that new_password and password2 match, and that new_password meets complexity requirements.
        """
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError('Password and confirm password are not the same.')

        if len(password) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')

        if ' ' in password:
            raise serializers.ValidationError('Password cannot contain spaces.')

        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&^#(){}[\]=+/\\|_\-<>])[A-Za-z\d@$!%*?&^#(){}[\]=+/\\|_\-<>]+$', password):
            raise serializers.ValidationError('Password must contain letters, numbers, and special characters.')

        return data

    def validate_old_password(self, old_password):
        user = self.context.get('user')
        if not check_password(old_password, user.password):
            raise serializers.ValidationError('Old password is incorrect.')

        return old_password

    def save(self):
        user = self.context.get('user')
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()    
    

class SetPasswordSerializer(serializers.Serializer):
    """
    Serializer for setting a new password without requiring the old password.
    """

    password = serializers.CharField(
        max_length=50, style={"input_type": "password"}, write_only=True, trim_whitespace=False
    )
    password2 = serializers.CharField(
        max_length=50, style={"input_type": "password"}, write_only=True, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and Authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            username = email,
            password = password
        )
        if not user:
            msg = _("Unable to authenticate user with provided credentials.")
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(style = {'input_type' : 'password'}, trim_whitespace = False)
