from django_filters import rest_framework as filters
from drf_yasg import openapi

from apps.accounting.models import Expense, MonthlyPayment


class YearMonthFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="paid_month__year")
    month = filters.NumberFilter(field_name="paid_month__month")

    class Meta:
        model = MonthlyPayment
        fields = ("year", "month")


class YearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="paid_month__year")

    class Meta:
        model = MonthlyPayment
        fields = ("year",)


class ExpenseFilter(filters.FilterSet):
    type = filters.NumberFilter(field_name="type")

    class Meta:
        model = Expense
        fields = ("type",)


YEAR_MONTH_FILTER_PARAMETERS = [
    openapi.Parameter("year", openapi.IN_QUERY, description="Year", type=openapi.TYPE_INTEGER, required=True),
    openapi.Parameter("month", openapi.IN_QUERY, description="Month", type=openapi.TYPE_INTEGER, required=True),
]

YEAR_FILTER_PARAMETERS = [
    openapi.Parameter("year", openapi.IN_QUERY, description="Year", type=openapi.TYPE_INTEGER, required=True),
]
