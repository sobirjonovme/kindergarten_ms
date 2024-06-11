from uuid import uuid4

import tablib
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from import_export import admin as ie_admin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from apps.organizations.choices import OrganizationTypes
from apps.organizations.models import EducatingGroup, Organization
from apps.users.choices import FaceIDLogTypes, UserTypes
from apps.users.models import FaceIDLog, User, UserPresence
from apps.users.tasks import send_user_info_to_hikvision

FACE_ID_COLUMN_NAME = "Face ID"


def make_sync_status_false(modeladmin, request, queryset):
    queryset.update(
        is_enter_terminal_synced=False,
        is_enter_image_synced=False,
        is_exit_terminal_synced=False,
        is_exit_image_synced=False,
    )


def fix_organization_via_group(modeladmin, request, queryset):
    for user in queryset:
        if user.educating_group and user.educating_group.organization:
            user.organization = user.educating_group.organization
            if user.organization.type == OrganizationTypes.SCHOOL:
                user.type = UserTypes.STUDENT
            elif user.organization.type == OrganizationTypes.KINDERGARTEN:
                user.type = UserTypes.KINDERGARTENER
            user.save(update_fields=["organization", "type"])
    modeladmin.message_user(request, str(_("Organization field is fixed")), messages.SUCCESS)


def sync_with_terminals(modeladmin, request, queryset):
    for user in queryset:
        send_user_info_to_hikvision.delay(user.id)

    modeladmin.message_user(request, str(_("Sending user info to Hikvision is in progress")), messages.WARNING)


class UserFaceImageFilter(admin.SimpleListFilter):
    title = _("has face image")
    parameter_name = "has_face_image"

    def lookups(self, request, model_admin):
        return (
            ("Yes", _("Yes")),
            ("No", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "Yes":
            qs_filter = Q(Q(face_image__isnull=False) & ~Q(face_image__exact=""))
            return queryset.filter(qs_filter)

        if self.value() == "No":
            qs_filter = Q(Q(face_image__isnull=True) | Q(face_image__exact=""))
            return queryset.filter(qs_filter)

        return queryset  # Default value


class FaceImageValidationFilter(admin.SimpleListFilter):
    title = _("Face Image Validation")
    parameter_name = "face_image_validation"

    def lookups(self, request, model_admin):
        return (
            ("enter_valid", _("Enter valid")),
            ("exit_valid", _("Exit valid")),
            ("both_valid", _("Both valid")),
            ("both_invalid", _("Both invalid")),
            ("enter_invalid", _("Enter invalid")),
            ("exit_invalid", _("Exit invalid")),
        )

    def queryset(self, request, queryset):
        # annotate face id log existence field to the queryset
        queryset = queryset.annotate(
            has_enter_log=Exists(
                FaceIDLog.objects.filter(user=OuterRef("pk"), type=FaceIDLogTypes.ENTER).values("id")[:1]
            ),
            has_exit_log=Exists(
                FaceIDLog.objects.filter(user=OuterRef("pk"), type=FaceIDLogTypes.EXIT).values("id")[:1]
            ),
        )
        value = self.value()

        if value == "enter_valid":
            qs_filter = Q(has_enter_log=True)
            return queryset.filter(qs_filter)
        elif value == "exit_valid":
            qs_filter = Q(has_exit_log=True)
            return queryset.filter(qs_filter)
        elif value == "both_valid":
            qs_filter = Q(has_enter_log=True) & Q(has_exit_log=True)
            return queryset.filter(qs_filter)
        elif value == "both_invalid":
            qs_filter = Q(has_enter_log=False) & Q(has_exit_log=False)
            return queryset.filter(qs_filter)
        elif value == "enter_invalid":
            qs_filter = Q(has_enter_log=False)
            return queryset.filter(qs_filter)
        elif value == "exit_invalid":
            qs_filter = Q(has_exit_log=False)
            return queryset.filter(qs_filter)

        return queryset  # Default value


class EnterTerminalFilter(admin.SimpleListFilter):
    title = _("Enter Terminal Sync")
    parameter_name = "enter_terminal_sync"

    def lookups(self, request, model_admin):
        return (
            ("Yes", _("Yes")),
            ("No", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "Yes":
            qs_filter = Q(Q(is_enter_terminal_synced=True) & Q(is_enter_image_synced=True))
            return queryset.filter(qs_filter)

        if self.value() == "No":
            qs_filter = Q(Q(is_enter_terminal_synced=False) | Q(is_enter_image_synced=False))
            return queryset.filter(qs_filter)

        return queryset  # Default value


class ExitTerminalFilter(admin.SimpleListFilter):
    title = _("Exit Terminal Sync")
    parameter_name = "exit_terminal_sync"

    def lookups(self, request, model_admin):
        return (
            ("Yes", _("Yes")),
            ("No", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "Yes":
            qs_filter = Q(Q(is_exit_terminal_synced=True) & Q(is_exit_image_synced=True))
            return queryset.filter(qs_filter)

        if self.value() == "No":
            qs_filter = Q(Q(is_exit_terminal_synced=False) | Q(is_exit_image_synced=False))
            return queryset.filter(qs_filter)

        return queryset  # Default value


class UserResource(resources.ModelResource):
    id = fields.Field(attribute="id", column_name="ID", readonly=True)
    first_name = fields.Field(attribute="first_name", column_name="Ism")
    last_name = fields.Field(attribute="last_name", column_name="Familiya")
    middle_name = fields.Field(attribute="middle_name", column_name="Otasining ismi")
    face_id = fields.Field(attribute="face_id", column_name=FACE_ID_COLUMN_NAME)
    type = fields.Field(attribute="type", column_name="Turi")
    organization = fields.Field(
        attribute="organization",
        column_name="Tashkilot ID",
        widget=ForeignKeyWidget(Organization, "id"),
    )
    educating_group = fields.Field(
        attribute="educating_group", column_name="Sinf/Guruh ID", widget=ForeignKeyWidget(EducatingGroup, "id")
    )

    def dehydrate_middle_name(self, user):
        return user.middle_name or ""

    def dehydrate_face_id(self, user):
        return user.face_id or ""

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "face_id",
            "type",
            "organization",
            "educating_group",
        )

    def export(self, queryset=None, **kwargs):
        """
        Exports a resource.

        :param queryset: The queryset for export (optional).

        :returns: A ``tablib.Dataset``.
        """
        self.before_export(queryset, **kwargs)

        if queryset is None:
            queryset = self.get_queryset()

        # order queryset by id
        queryset = queryset.order_by("id")

        queryset = self.filter_export(queryset, **kwargs)
        export_fields = kwargs.get("export_fields", None)
        headers = self.get_export_headers(fields=export_fields)
        dataset = tablib.Dataset(headers=headers)

        for obj in self.iter_queryset(queryset):
            r = self.export_resource(obj, fields=export_fields)
            dataset.append(r)

        self.after_export(queryset, dataset, **kwargs)

        return dataset

    def before_save_instance(self, instance, row, **kwargs):
        if not instance.pk:
            instance.username = User.generate_unique_username()
            instance.set_password(uuid4().hex)

    def before_import(self, dataset, **kwargs):
        """
        Check if any face_id in the dataset already exists in the database.
        """

        existing_face_ids = []
        for row in dataset.dict:
            if (
                row[FACE_ID_COLUMN_NAME]
                and User.objects.filter(face_id=row[FACE_ID_COLUMN_NAME]).exclude(id=row["ID"]).exists()
            ):
                existing_face_ids.append(row[FACE_ID_COLUMN_NAME])

        if existing_face_ids:
            duplicates = ", ".join(existing_face_ids)
            raise ValidationError(
                _("Quyidagi kiritilgan Face ID lar allaqachon ishlatilgan: %(duplicates)s") % {"duplicates": duplicates}
            )


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ()


@admin.register(User)
class UserAdmin(ie_admin.ImportExportMixin, ie_admin.ExportActionMixin, BaseUserAdmin):
    resource_class = UserResource
    show_change_form_export = False

    add_form = UserCreationForm
    actions = (sync_with_terminals, make_sync_status_false, fix_organization_via_group)

    list_display = (
        "id",
        "user_pic",
        "is_present_today",
        "first_name",
        "last_name",
        "middle_name",
        "educating_group",
        "organization",
        "face_id",
        "type",
        "terminal_1",
        "terminal_2",
        "parents_tg_ids",
    )
    list_editable = ("parents_tg_ids",)
    list_display_links = ("id", "first_name", "last_name", "middle_name", "face_id")
    search_fields = (
        "id",
        "first_name",
        "last_name",
        "middle_name",
        "face_id",
    )
    list_filter = (
        "type",
        "organization",
        "educating_group",
        UserFaceImageFilter,
        EnterTerminalFilter,
        ExitTerminalFilter,
        FaceImageValidationFilter,
    )
    ordering = ("-id",)
    autocomplete_fields = ("educating_group",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "middle_name",
                    "face_image",
                    "face_id",
                    "gender",
                    "salary",
                    "type",
                    "organization",
                    "educating_group",
                    "parents_tg_ids",
                )
            },
        ),
        (
            _("Hikvision Sync"),
            {
                "fields": (
                    "is_enter_terminal_synced",
                    "enter_terminal_sync_data",
                    "is_enter_image_synced",
                    "enter_image_sync_data",
                    "is_exit_terminal_synced",
                    "exit_terminal_sync_data",
                    "is_exit_image_synced",
                    "exit_image_sync_data",
                )
            },
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
                    "face_image",
                    "face_id",
                    "gender",
                    "type",
                    "organization",
                    "educating_group",
                ),
            },
        ),
    )

    def user_pic(self, obj):
        return mark_safe(
            '<a href="{url}"><img src="{url}" width="50" height="50" />'.format(
                url=obj.face_image.url if obj.face_image else "/static/images/default.png"
            )
        )

    user_pic.short_description = _("User pic")  # type: ignore

    def is_present_today(self, obj):
        is_present = bool(obj.is_present_today)
        return is_present

    is_present_today.short_description = _("Is present today")  # type: ignore
    is_present_today.boolean = True  # type: ignore

    def terminal_1(self, obj):
        is_complete = bool(obj.is_enter_terminal_synced and obj.is_enter_image_synced)
        return is_complete

    terminal_1.short_description = _("Terminal 1")  # type: ignore
    terminal_1.boolean = True  # type: ignore

    def terminal_2(self, obj):
        is_complete = bool(obj.is_exit_terminal_synced and obj.is_exit_image_synced)
        return is_complete

    terminal_2.short_description = _("Terminal 2")  # type: ignore
    terminal_2.boolean = True  # type: ignore

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("organization", "educating_group")
        day_start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        qs = qs.annotate(
            is_present_today=models.Exists(FaceIDLog.objects.filter(user=models.OuterRef("id"), time__gte=day_start))
        )
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.username = User.generate_unique_username()
            obj.set_password(uuid4().hex)
        super().save_model(request, obj, form, change)

        send_user_info_to_hikvision.delay(obj.id)


@admin.register(FaceIDLog)
class FaceIDLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "serial_no",
        "user",
        "type_",
        "time",
        "is_notified",
    )
    list_display_links = ("id", "serial_no", "user", "time")
    autocomplete_fields = ("user",)
    search_fields = ("id", "user__username", "user__first_name", "user__last_name")
    list_filter = ("created_at", "type", "is_notified")
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "time"

    def type_(self, obj):
        if not obj.type:
            return "-"

        type_colors = {
            # FaceIDLogTypes.ENTER: "#1fafed",
            # FaceIDLogTypes.IN_PROGRESS: "#3e484f",
            FaceIDLogTypes.ENTER: "green",
            FaceIDLogTypes.EXIT: "red",
        }
        return mark_safe(f'<span style="color: {type_colors[obj.type]}"><b>{obj.get_type_display()}</b></span>')

    type_.short_description = _("Type")  # type: ignore
    type_.admin_order_field = "type"  # type: ignore

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("user")
        return qs


@admin.register(UserPresence)
class UserPresenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "date",
        "present_time",
        "enter_at",
        "exit_at",
    )
    list_display_links = ("id", "user", "date")
    autocomplete_fields = ("user",)
    search_fields = ("id", "user__username", "user__first_name", "user__last_name", "user__middle_name")
    list_filter = ("enter_at",)
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "date"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("user")
        return qs
