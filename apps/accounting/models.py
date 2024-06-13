from django.core.exceptions import ValidationError
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
    is_notified = models.BooleanField(verbose_name=_("Is Notified"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), blank=True, null=True)
    # salary calculation fields for WORKERS
    present_days = models.IntegerField(verbose_name=_("Present Days"), blank=True, null=True)
    worked_hours = models.IntegerField(verbose_name=_("Worked Hours"), blank=True, null=True)
    total_working_days = models.IntegerField(verbose_name=_("Total Working Days"), blank=True, null=True)
    calculated_salary = models.DecimalField(
        verbose_name=_("Calculated Salary"), max_digits=13, decimal_places=2, blank=True, null=True
    )

    class Meta:
        verbose_name = _("Monthly Payment")
        verbose_name_plural = _("Monthly Payments")

    def __str__(self):
        return f"Fee #{self.id} - {self.user}"

    def clean(self):
        # Check if there is existing payment for the user in the same month
        if (
            MonthlyPayment.objects.filter(
                user=self.user, paid_month__year=self.paid_month.year, paid_month__month=self.paid_month.month
            )
            .exclude(id=self.id)
            .exists()
        ):
            raise ValidationError(
                message={
                    "user": _("User already has a payment for this month"),
                    "paid_month": _("User already has a payment for this month"),
                }
            )


class ExpenseType(BaseModel):
    """
    Model to store expense types
    """

    name = models.CharField(verbose_name=_("Name"), max_length=127, unique=True)

    class Meta:
        verbose_name = _("Expense Type")
        verbose_name_plural = _("Expense Types")

    def __str__(self):
        return self.name


class Expense(BaseModel):
    """
    Model to store expenses (outgoing money)
    """

    type = models.ForeignKey(
        verbose_name=_("Type"),
        to=ExpenseType,
        on_delete=models.SET_NULL,
        related_name="expenses",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(verbose_name=_("Amount"), max_digits=13, decimal_places=2)
    date = models.DateField(verbose_name=_("Date"), default=timezone.now)
    comment = models.TextField(verbose_name=_("Comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")

    def __str__(self):
        return f"Expense #{self.id} - {self.type}"
