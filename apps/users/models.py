from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel

from .choices import GenderTypes, UserTypes


# Create your models here.
class User(AbstractUser, BaseModel):
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    middle_name = models.CharField(_("Middle Name"), max_length=255, blank=True, null=True)
    gender = models.CharField(
        verbose_name=_("Gender"), max_length=31, choices=GenderTypes.choices, null=True, blank=True
    )
    type = models.CharField(_("Type"), max_length=31, choices=UserTypes.choices, default=UserTypes.ADMIN)
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

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        if self.first_name:
            name = self.first_name
            name += f" {self.last_name}" if self.last_name else ""
            name += f" {self.middle_name}" if self.middle_name else ""
            return name

        return self.username

    @classmethod
    def generate_unique_username(cls):
        username = str(uuid4().hex)[:30]
        while cls.objects.filter(username=username).exists():
            username = str(uuid4().hex)[:30]
        return username


class FaceIDLog(BaseModel):
    user = models.ForeignKey(verbose_name=_("User"), to="users.User", on_delete=models.CASCADE)
    time = models.DateTimeField(_("Time"), default=timezone.now)

    class Meta:
        verbose_name = _("Face ID Log")
        verbose_name_plural = _("Face ID Logs")

    def __str__(self):
        return f"FaceID | {self.user}"
