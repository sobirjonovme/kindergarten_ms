from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_jsonform.models.fields import ArrayField
from solo.models import SingletonModel

from apps.common.models import BaseModel
from apps.users.choices import UserTypes

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


class WorkCalendar(BaseModel):
    worker_type = models.CharField(verbose_name=_("Type"), max_length=31, choices=UserTypes.choices)
    month = models.DateField(verbose_name=_("Month"))
    work_days = ArrayField(
        verbose_name=_("Work Days"),
        base_field=models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)]),
        blank=True,
        null=True,
    )

    def clean(self):
        if self.month and self.month.day != 1:
            raise ValidationError({"month": _("Oyning birinchi kuni tanlanishi kerak")})

    class Meta:
        verbose_name = _("Work Calendar")
        verbose_name_plural = _("Work Calendars")
        unique_together = ("worker_type", "month")


class WorkingHourSettings(SingletonModel):
    last_calculation_date = models.DateField(verbose_name=_("Last Calculation Date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Working Hour Settings")
        verbose_name_plural = _("Working Hour Settings")

    def __str__(self):
        return str(_("Working Hour Settings"))
