from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from apps.users.models import FaceIDLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
    )
    list_display_links = ("id", "username", "first_name", "last_name")
    search_fields = ("id", "username", "first_name", "last_name")
    list_filter = ("is_active",)
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "middle_name", "type", "organization", "educating_group")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "middle_name",
                    "type",
                    "organization",
                    "educating_group",
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(FaceIDLog)
class FaceIDLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "time",
    )
    list_display_links = ("id", "user", "time")
    search_fields = ("id", "user__username", "user__first_name", "user__last_name")
    list_filter = ("created_at",)
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "time"
