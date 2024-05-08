from django.db import models
from django.utils.translation import gettext_lazy as _


class OrganizationTypes(models.TextChoices):
    SCHOOL = "school", _("School")
    KINDERGARTEN = "kindergarten", _("Kindergarten")
