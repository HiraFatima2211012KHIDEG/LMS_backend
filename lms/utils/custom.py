from rest_framework.response import Response
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

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
    permission_classes = [permissions.IsAuthenticated]

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
