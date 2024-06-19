from django.contrib import admin
from solo.admin import SingletonModelAdmin

from apps.accounting.tasks import calculate_workers_salaries

from .models import (EducatingGroup, Organization, WorkCalendar,
                     WorkingHourSettings)


# custom actions
def recalculate_workers_salaries(modeladmin, request, queryset):
    for work_calendar in queryset:
        calculate_workers_salaries.delay(month_date=work_calendar.month)


# Register your models here.
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    search_fields = ("id", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EducatingGroup)
class EducatingGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "organization")
    list_display_links = ("id", "name", "organization")
    list_filter = ("organization",)
    ordering = ("-id",)
    search_fields = (
        "id",
        "name",
    )
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("organization")
        return qs


@admin.register(WorkCalendar)
class WorkCalendarAdmin(admin.ModelAdmin):
    actions = (recalculate_workers_salaries,)

    list_display = ("id", "worker_type", "month", "work_days")
    list_display_links = ("id", "worker_type", "month")
    list_filter = ("worker_type",)
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        obj.save()
        calculate_workers_salaries.delay(month_date=obj.month)


@admin.register(WorkingHourSettings)
class WorkingHourSettingsAdmin(SingletonModelAdmin):
    pass
