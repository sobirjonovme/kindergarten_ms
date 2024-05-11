from django.db import models
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from apps.accounting.filters import (YEAR_MONTH_FILTER_PARAMETERS,
                                     YearMonthFilter)
from apps.accounting.models import MonthlyPayment
from apps.users.filters import USER_FILTER_PARAMETERS, UserFilter
from apps.users.models import User
from apps.users.permissions import IsAdminUser

from .serializers import UsersMonthlyPaymentListSerializer

USERS_PAYMENT_FILTER_PARAMETERS = [
    *USER_FILTER_PARAMETERS,
    *YEAR_MONTH_FILTER_PARAMETERS,
]


class UsersMonthlyPaymentListAPIView(ListAPIView):
    """
    API endpoint to get the list TUITION FEES and SALARIES
    type description:
    - TUITION_FEE  ->  for students tuition fees
    - SALARY  ->  for workers salaries
    """

    serializer_class = UsersMonthlyPaymentListSerializer
    permission_classes = (IsAdminUser,)

    total_payment = 0

    def get_queryset(self):
        users = User.objects.all()
        users = UserFilter(data=self.request.query_params, queryset=users).qs

        users = users.prefetch_related(
            models.Prefetch(
                "monthly_payments",
                queryset=YearMonthFilter(data=self.request.query_params, queryset=MonthlyPayment.objects.all()).qs,
            ),
        )

        # calculate total amount of payment
        self.total_payment = YearMonthFilter(
            data=self.request.query_params, queryset=MonthlyPayment.objects.filter(user__in=users)
        ).qs.aggregate(total_payment=models.Sum("amount"))["total_payment"]

        return users

    @swagger_auto_schema(manual_parameters=USERS_PAYMENT_FILTER_PARAMETERS)
    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)

        if isinstance(res.data, list):
            res.data = {
                "total_payment": self.total_payment,
                "data": res.data,
            }
        elif isinstance(res.data, dict):
            res.data = {"total_payment": self.total_payment, **res.data}

        return res


__all__ = ["UsersMonthlyPaymentListAPIView"]
