from rest_framework.response import Response
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db import models

STATUS_CHOICES = (
    (0, "Not Active"),
    (1, "Active"),
    (2, "Deleted"),
)


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
        # Filter the queryset to only return records with status 0 or 1
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
    # Update the status of the parent instance first
    instance.status = new_status
    # instance.save()

    # Iterate over related models
    for rel in instance._meta.related_objects:
        related_model = rel.related_model
        field_name = rel.field.name

        # Check if the related model has a 'status' field
        if hasattr(related_model, "status"):
            # Handle ForeignKey relationships
            if isinstance(rel, models.ManyToOneRel):  # ForeignKey
                related_objects = related_model.objects.filter(**{field_name: instance})
                related_objects.update(status=new_status)

            # Handle ManyToManyField relationships
            elif isinstance(rel, models.ManyToManyRel):  # ManyToManyField
                related_objects = getattr(instance, rel.get_accessor_name()).all()
                for obj in related_objects:
                    obj.status = new_status
                    obj.save()
