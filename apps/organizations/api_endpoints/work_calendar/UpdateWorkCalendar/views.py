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

        today = timezone.localdate()
        if obj.month.month != today.month and obj.month.year != today.year:
            raise ValidationError(_("Only current month's work calendar can be updated"))

        return obj


__all__ = ["WorkCalendarUpdateAPIView"]
