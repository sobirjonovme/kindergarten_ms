from django.db import models
from django.utils.translation import gettext_lazy as _


class MonthlyPaymentTypes(models.TextChoices):
    TUITION_FEE = "tuition_fee", _("Tuition Fee")
    SALARY = "salary", _("Salary")
