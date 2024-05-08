from django.contrib import admin

from .models import EducatingGroup, Organization


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
    search_fields = (
        "id",
        "name",
    )
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("organization")
        return qs
