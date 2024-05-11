from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel

from .choices import MonthlyPaymentTypes


# Create your models here.
class MonthlyPayment(BaseModel):
    """
    Model to store monthly payments
    for: STUDENTS TUITION FEES and WORKERS SALARIES
    """

    type = models.CharField(verbose_name=_("Type"), max_length=31, choices=MonthlyPaymentTypes.choices)
    user = models.ForeignKey(
        verbose_name=_("User"),
        to="users.User",
        on_delete=models.SET_NULL,
        related_name="monthly_payments",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(verbose_name=_("Amount"), max_digits=13, decimal_places=2)
    paid_month = models.DateField(verbose_name=_("Paid Date"), default=timezone.now)
    is_completed = models.BooleanField(verbose_name=_("Is Completed"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("Monthly Payment")
        verbose_name_plural = _("Monthly Payments")

    def __str__(self):
        return f"Fee #{self.id} - {self.user}"
