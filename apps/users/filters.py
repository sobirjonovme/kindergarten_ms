from django.db.models import Q
from django_filters import rest_framework as filters
from drf_yasg import openapi

from apps.users.choices import UserShortTypes, UserTypes
from apps.users.models import FaceIDLog, User


class UserFilter(filters.FilterSet):
    organization = filters.NumberFilter(field_name="organization")
    educating_group = filters.NumberFilter(field_name="educating_group")
    # types: student, worker
    type = filters.ChoiceFilter(choices=UserShortTypes.choices, method="filter_type")

    has_face_image = filters.BooleanFilter(method="filter_image")
    is_terminals_synced = filters.BooleanFilter(method="filter_terminal")

    class Meta:
        model = User
        fields = ("organization", "educating_group", "type", "has_face_image", "is_terminals_synced")

    def filter_type(self, queryset, name, value):
        if value == UserShortTypes.STUDENT:
            type_list = UserTypes.get_student_types()
            return queryset.filter(type__in=type_list)
        elif value == UserShortTypes.WORKER:
            type_list = UserTypes.get_worker_types()
            return queryset.filter(type__in=type_list)
        return queryset

    def filter_image(self, queryset, name, value):
        if value:
            queryset = queryset.filter(Q(face_image__isnull=False) & ~Q(face_image__exact=""))
        else:
            queryset = queryset.filter(Q(face_image__isnull=True) | Q(face_image__exact=""))

        return queryset

    def filter_terminal(self, queryset, name, value):
        full_synced_filter = Q(
            is_enter_terminal_synced=True,
            is_enter_image_synced=True,
            is_exit_terminal_synced=True,
            is_exit_image_synced=True,
        )
        if value:
            queryset = queryset.filter(full_synced_filter)
        else:
            queryset = queryset.exclude(full_synced_filter)

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

USER_MANAGEMENT_FILTER_PARAMETERS = [
    *USER_FILTER_PARAMETERS,
    openapi.Parameter("has_face_image", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False),
    openapi.Parameter("is_terminals_synced", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False),
]
