"""
Views for the Accounts Applications API.
"""
from rest_framework import generics
from ..serializers.application_serializers import ApplicationSerializer


class CreateApplicationView(generics.CreateAPIView):
    """Create a new user in the application."""
    serializer_class = ApplicationSerializer