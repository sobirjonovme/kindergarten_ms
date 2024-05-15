from django_filters import rest_framework as filters
from drf_yasg import openapi

from apps.accounting.models import Expense, MonthlyPayment


class MonthlyPaymentFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name="paid_month", lookup_expr="gte")
    to_date = filters.DateFilter(field_name="paid_month", lookup_expr="lte")
    year = filters.NumberFilter(field_name="paid_month__year")
    month = filters.NumberFilter(field_name="paid_month__month")

    class Meta:
        model = MonthlyPayment
        fields = ("from_date", "to_date", "year", "month")


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

DATE_RANGE_FILTER_PARAMETERS = [
    openapi.Parameter("from_date", openapi.IN_QUERY, description="From date", type=openapi.TYPE_STRING, required=True),
    openapi.Parameter("to_date", openapi.IN_QUERY, description="To date", type=openapi.TYPE_STRING),
]
