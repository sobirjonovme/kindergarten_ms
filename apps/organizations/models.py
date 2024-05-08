from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel

from .choices import OrganizationTypes


# Create your models here.
class Organization(BaseModel):
    name = models.CharField(max_length=255)
    type = models.CharField(_("Type"), max_length=31, choices=OrganizationTypes.choices)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return self.name


class EducatingGroup(BaseModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(verbose_name=_("Organization"), to=Organization, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Educating Group")
        verbose_name_plural = _("Educating Groups")

    def __str__(self):
        return self.name
