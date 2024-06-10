from rest_framework.generics import CreateAPIView

from apps.organizations.models import WorkCalendar
from apps.users.permissions import IsAdminUser

from .serializers import CreateWorkCalendarSerializer


class WorkCalendarCreateAPIView(CreateAPIView):
    queryset = WorkCalendar.objects.all()
    serializer_class = CreateWorkCalendarSerializer
    permission_classes = (IsAdminUser,)


__all__ = ["WorkCalendarCreateAPIView"]
