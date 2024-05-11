from rest_framework.generics import ListAPIView

from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationShortSerializer
from apps.users.permissions import IsAdminUser


class OrganizationListAPIView(ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationShortSerializer
    permission_classes = (IsAdminUser,)

    pagination_class = None


__all__ = ["OrganizationListAPIView"]
