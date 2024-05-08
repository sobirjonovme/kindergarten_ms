from django_filters import rest_framework as filters
from drf_yasg import openapi

from apps.users.choices import UserShortTypes, UserTypes
from apps.users.models import FaceIDLog, User


class UserFilter(filters.FilterSet):
    organization = filters.NumberFilter(field_name="organization")
    educating_group = filters.NumberFilter(field_name="educating_group")
    # types: student, worker
    type = filters.ChoiceFilter(choices=UserShortTypes.choices, method="filter_type")

    class Meta:
        model = User
        fields = ("organization", "educating_group", "type")

    def filter_type(self, queryset, name, value):
        if value == UserShortTypes.STUDENT:
            type_list = UserTypes.get_student_types()
            return queryset.filter(type__in=type_list)
        elif value == UserShortTypes.WORKER:
            type_list = UserTypes.get_worker_types()
            return queryset.filter(type__in=type_list)
        return queryset


class AttendanceDateFilter(filters.FilterSet):
    date = filters.DateFilter(field_name="time__date")

    class Meta:
        model = FaceIDLog
        fields = ("date",)


USER_FILTER_PARAMETERS = [
    openapi.Parameter("organization", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    openapi.Parameter("educating_group", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    openapi.Parameter("type", openapi.IN_QUERY, type=openapi.TYPE_STRING, enum=UserShortTypes.values),
]

ATTENDANCE_FILTER_PARAMETERS = [
    openapi.Parameter("date", openapi.IN_QUERY, type=openapi.FORMAT_DATE, required=False),
    *USER_FILTER_PARAMETERS,
]
