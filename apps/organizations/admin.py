from django.contrib import admin

from .models import EducatingGroup, Organization, WorkCalendar


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
    list_display = ("id", "worker_type", "month", "daily_work_hours", "work_days")
    list_display_links = ("id", "worker_type", "month", "daily_work_hours")
    list_filter = ("worker_type",)
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")
