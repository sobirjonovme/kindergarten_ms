from rest_framework import serializers

from apps.accounting.tasks import calculate_workers_salaries
from apps.organizations.models import WorkCalendar


class UpdateWorkCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCalendar
        fields = (
            "id",
            "work_days",
        )

    def save(self, **kwargs):
        work_calendar = super().save(**kwargs)

        calculate_workers_salaries.delay(work_calendar.month)

        return work_calendar
