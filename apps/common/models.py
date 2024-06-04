from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # add updated_at field to update_fields if it is not present
        # so that updated_at field will always be updated
        if update_fields and "updated_at" not in update_fields:
            update_fields.append("updated_at")

        super().save(force_insert, force_update, using, update_fields)


class VersionHistory(BaseModel):
    version = models.CharField(_("Version"), max_length=64)
    required = models.BooleanField(_("Required"), default=True)

    class Meta:
        verbose_name = _("Version history")
        verbose_name_plural = _("Version histories")

    def __str__(self):
        return self.version


class FrontendTranslation(BaseModel):
    key = models.CharField(_("Key"), max_length=255, unique=True)
    text = models.CharField(_("Text"), max_length=1024)

    class Meta:
        verbose_name = _("Frontend translation")
        verbose_name_plural = _("Frontend translations")

    def __str__(self):
        return str(self.key)


class FaceIDSettings(SingletonModel):
    # enter device
    enter_device_ip = models.CharField(_("Enter device IP"), max_length=255, blank=True, null=True)
    enter_device_last_sync_time = models.DateTimeField(_("Enter device last sync time"), blank=True, null=True)
    enter_device_username = models.CharField(_("Enter device username"), max_length=255, blank=True, null=True)
    enter_device_password = models.CharField(_("Enter device password"), max_length=255, blank=True, null=True)
    enter_last_run = models.DateTimeField(_("Enter last run"), blank=True, null=True)
    # exit device
    exit_device_ip = models.CharField(_("Exit device IP"), max_length=255, blank=True, null=True)
    exit_device_last_sync_time = models.DateTimeField(_("Exit device last sync time"), blank=True, null=True)
    exit_device_username = models.CharField(_("Exit device username"), max_length=255, blank=True, null=True)
    exit_device_password = models.CharField(_("Exit device password"), max_length=255, blank=True, null=True)
    exit_last_run = models.DateTimeField(_("Exit last run"), blank=True, null=True)

    class Meta:
        verbose_name = _("Face ID settings")
        verbose_name_plural = _("Face ID settings")

    def __str__(self):
        return str(_("Face ID settings"))
