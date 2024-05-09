from rest_framework.generics import ListAPIView

from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationShortSerializer


class OrganizationListAPIView(ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationShortSerializer

    pagination_class = None


__all__ = ["OrganizationListAPIView"]
