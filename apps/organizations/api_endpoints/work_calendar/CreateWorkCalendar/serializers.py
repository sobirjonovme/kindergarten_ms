from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.organizations.models import WorkCalendar


class CreateWorkCalendarSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(
        write_only=True, required=True, allow_null=False, validators=[MinValueValidator(2023)]
    )
    month = serializers.IntegerField(
        write_only=True, required=True, allow_null=False, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    class Meta:
        model = WorkCalendar
        fields = (
            "id",
            "worker_type",
            "year",
            "month",
            "work_days",
        )

    def validate(self, data):
        year = data.pop("year", None)
        data["month"] = f"{year}-{data['month']}-01"

        # check if the work calendar already exists with the same worker type and month
        if WorkCalendar.objects.filter(worker_type=data["worker_type"], month=data["month"]).exists():
            raise serializers.ValidationError(_("Work calendar already exists"))

        return data
