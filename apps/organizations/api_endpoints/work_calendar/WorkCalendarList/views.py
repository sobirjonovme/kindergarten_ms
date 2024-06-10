from rest_framework.generics import ListAPIView

from apps.organizations.models import WorkCalendar
from apps.organizations.serializers import WorkCalendarDetailSerializer
from apps.users.permissions import IsAdminUser


class WorkCalendarListAPIView(ListAPIView):
    queryset = WorkCalendar.objects.all().order_by("-month")
    serializer_class = WorkCalendarDetailSerializer
    permission_classes = (IsAdminUser,)


__all__ = ["WorkCalendarListAPIView"]
