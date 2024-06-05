from uuid import uuid4

import tablib
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from import_export import admin as ie_admin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from apps.organizations.models import EducatingGroup, Organization
from apps.users.models import FaceIDLog, User
from apps.users.tasks import send_user_info_to_hikvision

FACE_ID_COLUMN_NAME = "Face ID"


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

    list_display = (
        "id",
        "first_name",
        "last_name",
        "middle_name",
        "face_id",
        "organization",
        "educating_group",
        "type",
    )
    list_display_links = ("id", "first_name", "last_name", "middle_name", "face_id")
    search_fields = (
        "id",
        "first_name",
        "last_name",
        "middle_name",
        "face_id",
    )
    list_filter = ("type", "organization", "educating_group")
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
                    "face_id",
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

        send_user_info_to_hikvision.delay(obj.id)


@admin.register(FaceIDLog)
class FaceIDLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "serial_no",
        "user",
        "type",
        "time",
        "is_notified",
    )
    list_display_links = ("id", "serial_no", "user", "time")
    search_fields = ("id", "user__username", "user__first_name", "user__last_name")
    list_filter = ("created_at", "type", "is_notified")
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "time"
