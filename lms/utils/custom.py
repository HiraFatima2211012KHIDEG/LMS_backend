from rest_framework.response import Response
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.contrib.auth.hashers import check_password
from django.db import models
from datetime import timedelta
import re


class CustomResponseMixin:
    def custom_response(self, status_code, message, data):
        return Response(
            {"status_code": status_code, "message": message, "data": data},
            status=status_code,
        )


class BaseLocationViewSet(
    CustomResponseMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    #    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(status__in=[0, 1])

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_201_CREATED, "created successfully", response.data
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.custom_response(
            status.HTTP_200_OK, "updated successfully", response.data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 2
        instance.save()
        return self.custom_response(
            status.HTTP_204_NO_CONTENT, "deleted successfully", None
        )


def custom_extend_schema(serializer):
    return extend_schema(
        request=serializer,
        responses={200: "successful", 400: "Bad Request."},
    )


def cascade_status_change(instance, new_status):
    """
    General function to cascade status changes to all related objects.

    Args:
        instance: The parent model instance whose status is changing.
        new_status: The new status value to be applied to the instance and related objects.
    """
    instance.status = new_status
    for rel in instance._meta.related_objects:
        related_model = rel.related_model
        field_name = rel.field.name

        if hasattr(related_model, "status"):
            if isinstance(rel, models.ManyToOneRel):
                related_objects = related_model.objects.filter(**{field_name: instance})
                related_objects.update(status=new_status)

            elif isinstance(rel, models.ManyToManyRel):
                related_objects = getattr(instance, rel.get_accessor_name()).all()
                for obj in related_objects:
                    obj.status = new_status
                    obj.save()


def get_assessment(self, obj, Model):
    model = Model.objects.filter(
        course=obj.course, due_date__range=[obj.start_date, obj.end_date]
    )
    return [
        {
            "name": assessment.question,
            "due_date": assessment.due_date.strftime("%Y-%m-%d"),
            "due_time": assessment.due_date.strftime("%H:%M"),
        }
        for assessment in model
    ]


def get_dates_from_days(self, start_date, end_date, days_of_week):
    """Generate a list of dates based on start and end dates and specified days of the week."""
    current_date = start_date
    actual_dates = []

    # Iterate through each day in the range
    while current_date <= end_date:
        if current_date.weekday() in days_of_week:
            actual_dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    return actual_dates


def validate_password(self, value):
    """
    Validate that new_password and password2 match, and that new_password meets complexity requirements.
    """
    password = value.get("password")
    password2 = value.get("password2")
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

    return value
