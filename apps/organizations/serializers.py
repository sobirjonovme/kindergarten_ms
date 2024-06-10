from rest_framework import serializers

from .models import EducatingGroup, Organization, WorkCalendar


class OrganizationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")


class EducatingGroupShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducatingGroup
        fields = ("id", "name")


class WorkCalendarDetailSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(source="month.year")
    month = serializers.IntegerField(source="month.month")

    class Meta:
        model = WorkCalendar
        fields = (
            "id",
            "worker_type",
            "year",
            "month",
            "daily_work_hours",
            "work_days",
        )
