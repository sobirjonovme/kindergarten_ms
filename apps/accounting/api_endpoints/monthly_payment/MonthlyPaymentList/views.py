from django.db import models
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.validators import ValidationError

from apps.accounting.filters import (YEAR_MONTH_FILTER_PARAMETERS,
                                     MonthlyPaymentFilter)
from apps.accounting.models import MonthlyPayment
from apps.organizations.models import WorkCalendar
from apps.users.choices import UserShortTypes, UserTypes
from apps.users.filters import USER_FILTER_PARAMETERS, UserFilter
from apps.users.models import User
from apps.users.permissions import IsAdminUser

from .serializers import (UsersMonthlyPaymentListSerializer,
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

    total_payment = 0

    def get_serializer_class(self):
        user_type = self.request.query_params.get("type")
        if user_type == UserShortTypes.WORKER:
            return WorkerSalaryListSerializer
        return UsersMonthlyPaymentListSerializer

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
        users = users.annotate(
            present_days=models.Count(
                "user_presences",
                filter=models.Q(user_presences__date__year=year, user_presences__date__month=month),
                distinct=True,
            ),
        )

        # calculate total amount of payment
        self.total_payment = MonthlyPaymentFilter(
            data=self.request.query_params, queryset=MonthlyPayment.objects.filter(user__in=users)
        ).qs.aggregate(total_payment=models.Sum("amount"))["total_payment"]

        teacher_work_calendar = WorkCalendar.objects.filter(
            worker_type=UserTypes.TEACHER, month__year=year, month__month=month
        ).first()
        educator_work_calendar = WorkCalendar.objects.filter(
            worker_type=UserTypes.EDUCATOR, month__year=year, month__month=month
        ).first()

        # calculate total working hours
        if user_type == UserShortTypes.WORKER and teacher_work_calendar and educator_work_calendar:
            teacher_working_hours = teacher_work_calendar.daily_work_hours * len(teacher_work_calendar.work_days)
            educator_working_hours = educator_work_calendar.daily_work_hours * len(educator_work_calendar.work_days)

            users = users.annotate(
                worked_hours=models.Case(
                    models.When(
                        type=UserTypes.TEACHER,
                        then=models.Sum(
                            "user_presences__present_time",
                            filter=models.Q(
                                user_presences__date__year=year,
                                user_presences__date__month=month,
                                user_presences__date__day__in=teacher_work_calendar.work_days,
                            ),
                        ),
                    ),
                    models.When(
                        type=UserTypes.EDUCATOR,
                        then=models.Sum(
                            "user_presences__present_time",
                            filter=models.Q(
                                user_presences__date__year=year,
                                user_presences__date__month=month,
                                user_presences__date__day__in=educator_work_calendar.work_days,
                            ),
                        ),
                    ),
                    default=models.Value(0),
                ),
                total_working_hours=models.Case(
                    models.When(type=UserTypes.TEACHER, then=models.Value(teacher_working_hours)),
                    models.When(type=UserTypes.EDUCATOR, then=models.Value(educator_working_hours)),
                    default=models.Value(0),
                ),
            )

            users = users.annotate(
                worked_hours=models.Sum(
                    "user_presences__present_time",
                    filter=models.Q(user_presences__date__year=year, user_presences__date__month=month),
                ),
            )

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
                "data": res.data,
            }
        elif isinstance(res.data, dict):
            res.data = {"total_payment": self.total_payment, **res.data}

        return res


__all__ = ["UsersMonthlyPaymentListAPIView"]
