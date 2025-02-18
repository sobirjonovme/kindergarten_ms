from django.db import models
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.validators import ValidationError
from rest_framework.filters import SearchFilter

from apps.accounting.filters import (YEAR_MONTH_FILTER_PARAMETERS,
                                     MonthlyPaymentFilter)
from apps.accounting.models import MonthlyPayment
from apps.users.choices import UserShortTypes
from apps.users.filters import USER_FILTER_PARAMETERS, UserFilter
from apps.users.models import User
from apps.users.permissions import IsAdminUser

from .serializers import (StudentsMonthlyPaymentListSerializer,
                          WorkerSalaryListSerializer)

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

    # serializer_class = UsersMonthlyPaymentListSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (SearchFilter,)
    search_fields = ("first_name", "last_name", "middle_name")

    total_payment = 0
    total_payments_number = 0

    def get_serializer_class(self):
        user_type = self.request.query_params.get("type")

        # check if user_type is WORKER
        if user_type == UserShortTypes.WORKER:
            return WorkerSalaryListSerializer

        # so it is a student
        return StudentsMonthlyPaymentListSerializer

    def get_queryset(self):
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")
        user_type = self.request.query_params.get("type")

        users = User.objects.order_by("first_name", "last_name", "middle_name")
        users = UserFilter(data=self.request.query_params, queryset=users).qs

        users = users.prefetch_related(
            models.Prefetch(
                "monthly_payments",
                queryset=MonthlyPaymentFilter(data=self.request.query_params, queryset=MonthlyPayment.objects.all()).qs,
            ),
        )
        if user_type == UserShortTypes.STUDENT:
            users = users.annotate(
                present_days=models.Count(
                    "user_presences",
                    filter=models.Q(user_presences__date__year=year, user_presences__date__month=month),
                    distinct=True,
                ),
            )

        # calculate total amount of payment
        monthly_payments = MonthlyPaymentFilter(
            data=self.request.query_params, queryset=MonthlyPayment.objects.filter(user__in=users)
        ).qs

        self.total_payment = monthly_payments.aggregate(total_payment=models.Sum("amount"))["total_payment"]
        self.total_payments_number = len(set(monthly_payments.values_list("user", flat=True)))

        return users

    @swagger_auto_schema(manual_parameters=USERS_PAYMENT_FILTER_PARAMETERS)
    def get(self, request, *args, **kwargs):
        # check if YEAR and MONTH are provided in the query parameters
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        user_type = request.query_params.get("type")
        if not year or not month:
            raise ValidationError(
                code="required",
                detail={"year_month": ["Both year and month are required in the query parameters."]},
            )
        if not user_type:
            raise ValidationError(
                code="required",
                detail={"type": ["User type is required in the query parameters."]},
            )

        res = super().get(request, *args, **kwargs)

        if isinstance(res.data, list):
            res.data = {
                "total_payment": self.total_payment,
                "total_payments_number": self.total_payments_number,
                "data": res.data,
            }
        elif isinstance(res.data, dict):
            res.data = {
                "total_payment": self.total_payment,
                "total_payments_number": self.total_payments_number,
                **res.data,
            }

        return res


__all__ = ["UsersMonthlyPaymentListAPIView"]
