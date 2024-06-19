from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import UpdateAPIView
from rest_framework.validators import ValidationError

from apps.organizations.models import WorkCalendar
from apps.users.permissions import IsAdminUser

from .serializers import UpdateWorkCalendarSerializer


class WorkCalendarUpdateAPIView(UpdateAPIView):
    """
    Update work calendar
    Only current month's work calendar can be updated
    """

    queryset = WorkCalendar.objects.all()
    serializer_class = UpdateWorkCalendarSerializer
    permission_classes = (IsAdminUser,)

    def get_object(self):
        obj = super().get_object()

        current_month_start = timezone.localdate().replace(day=1)
        if obj.month < current_month_start:
            raise ValidationError(_("Only current or future month's work calendar can be updated"))

        return obj


__all__ = ["WorkCalendarUpdateAPIView"]
