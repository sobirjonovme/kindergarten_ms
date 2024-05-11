from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from apps.organizations.models import EducatingGroup
from apps.organizations.serializers import EducatingGroupShortSerializer
from apps.users.permissions import IsAdminUser


class EducatingGroupListAPIView(ListAPIView):
    queryset = EducatingGroup.objects.order_by("name")
    serializer_class = EducatingGroupShortSerializer
    permission_classes = (IsAdminUser,)

    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("organization",)


__all__ = ["EducatingGroupListAPIView"]
