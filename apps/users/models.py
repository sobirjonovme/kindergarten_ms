from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_jsonform.models.fields import ArrayField

from apps.common.models import BaseModel

from .choices import FaceIDLogTypes, GenderTypes, UserTypes


# Create your models here.
class User(AbstractUser, BaseModel):
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    middle_name = models.CharField(_("Middle Name"), max_length=255, blank=True, null=True)
    face_image = models.ImageField(
        verbose_name=_("Face Image"),
        upload_to="face_images",
        help_text=_("Image size should be less than 200KB"),
        blank=True,
        null=True,
    )

    # Face ID terminal fields
    face_id = models.CharField(_("Face ID"), max_length=255, null=True)
    # face_id must be unique
    is_enter_terminal_synced = models.BooleanField(_("Is Synced with Enter Terminal"), default=False)
    enter_terminal_sync_data = models.TextField(verbose_name=_("Enter Terminal Sync Data"), blank=True, null=True)
    is_enter_image_synced = models.BooleanField(_("Is Image Synced with Enter Terminal"), default=False)
    enter_image_sync_data = models.TextField(verbose_name=_("Enter Image Sync Data"), blank=True, null=True)
    is_exit_terminal_synced = models.BooleanField(_("Is Synced with Exit Terminal"), default=False)
    exit_terminal_sync_data = models.TextField(verbose_name=_("Exit Terminal Sync Data"), blank=True, null=True)
    is_exit_image_synced = models.BooleanField(_("Is Image Synced with Exit Terminal"), default=False)
    exit_image_sync_data = models.TextField(verbose_name=_("Exit Image Sync Data"), blank=True, null=True)
    # End of Face ID terminal fields

    gender = models.CharField(
        verbose_name=_("Gender"), max_length=31, choices=GenderTypes.choices, null=True, blank=True
    )
    type = models.CharField(_("Type"), max_length=31, choices=UserTypes.choices, default=UserTypes.ADMIN)
    salary = models.DecimalField(_("Salary"), max_digits=13, decimal_places=2, null=True, blank=True)
    organization = models.ForeignKey(
        verbose_name=_("Organization"), to="organizations.Organization", on_delete=models.CASCADE, blank=True, null=True
    )
    educating_group = models.ForeignKey(
        verbose_name=_("Educating Group"),
        to="organizations.EducatingGroup",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    parents_tg_ids = ArrayField(
        verbose_name=_("Parents Telegram IDs"),
        base_field=models.CharField(max_length=31, blank=True, null=True),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        name = self.username

        if self.first_name:
            name = self.first_name
            name += f" {self.last_name}" if self.last_name else ""
            name += f" {self.middle_name}" if self.middle_name else ""

        return f"#{self.id} | {name}"

    def clean(self):
        # check face_id uniqueness
        if self.face_id and User.objects.filter(face_id=self.face_id).exclude(id=self.id).exists():
            raise ValidationError({"face_id": _("Kiritilgan Face ID allaqachon ishlatilgan")})

        # check face image size less than 200KB
        if self.face_image and self.face_image.size > 200 * 1024:
            raise ValidationError({"face_image": _("Rasm hajmi 200KB dan kam bo'lishi kerak")})

    def generate_full_name(self):
        full_name = self.first_name
        full_name += f" {self.last_name}" if self.last_name else ""
        return full_name

    @classmethod
    def generate_unique_username(cls):
        username = str(uuid4().hex)[:30]
        while cls.objects.filter(username=username).exists():
            username = str(uuid4().hex)[:30]
        return username


class FaceIDLog(BaseModel):
    user = models.ForeignKey(verbose_name=_("User"), to="users.User", on_delete=models.CASCADE)
    type = models.CharField(_("Type"), max_length=31, choices=FaceIDLogTypes.choices, null=True, blank=True)
    time = models.DateTimeField(_("Time"), default=timezone.now)
    serial_no = models.CharField(_("Serial No"), max_length=255, blank=True, null=True)
    log_data = models.JSONField(_("Log Data"), blank=True, null=True)
    is_notified = models.BooleanField(_("Is Notified"), default=False)
    notification_log = models.TextField(verbose_name=_("Notification Log"), blank=True, null=True)

    class Meta:
        verbose_name = _("Face ID Log")
        verbose_name_plural = _("Face ID Logs")

    def __str__(self):
        return f"FaceID #{self.id} | {self.user}"


class UserPresence(BaseModel):
    user = models.ForeignKey(verbose_name=_("User"), to=User, on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"))
    enter_at = models.TimeField(verbose_name=_("Enter at"), blank=True, null=True)
    exit_at = models.TimeField(verbose_name=_("Exit at"), blank=True, null=True)
    present_time = models.PositiveIntegerField(verbose_name=_("Present Time"), help_text=_("in hours"), default=0)

    class Meta:
        verbose_name = _("User Presence")
        verbose_name_plural = _("User Presences")
        unique_together = ("user", "date")

    def __str__(self):
        return f"Presence #{self.id} - {self.user}"
