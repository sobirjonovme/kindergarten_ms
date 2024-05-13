from uuid import uuid4

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from apps.users.models import FaceIDLog, User


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm

    list_display = (
        "id",
        "type",
        "first_name",
        "last_name",
        "middle_name",
        "organization",
        "educating_group",
    )
    list_display_links = ("id", "first_name", "last_name", "middle_name")
    search_fields = (
        "id",
        "first_name",
        "last_name",
        "middle_name",
    )
    list_filter = ("type", "organization", "educating_group")
    ordering = ("-id",)
    autocomplete_fields = ("educating_group",)
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
                    "gender",
                    "type",
                    "organization",
                    "educating_group",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("organization", "educating_group")
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.username = User.generate_unique_username()
            obj.set_password(uuid4().hex)
        super().save_model(request, obj, form, change)


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
