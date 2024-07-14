from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView

from apps.common.pagination import CustomPagination100
from apps.users.filters import USER_MANAGEMENT_FILTER_PARAMETERS, UserFilter
from apps.users.models import User
from apps.users.permissions import IsAdminUser

from .serializers import UserListSerializer


class UserListAPIView(ListAPIView):
    serializer_class = UserListSerializer
    pagination_class = CustomPagination100
    permission_classes = (IsAdminUser,)

    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = UserFilter
    search_fields = ("first_name", "last_name", "middle_name")

    def get_queryset(self):
        users_qs = User.objects.order_by("first_name", "last_name", "middle_name")

        # add Terminals status
        # enter_terminal_synced: boolean = is_enter_terminal_synced and is_enter_image_synced
        # exit_terminal_synced: boolean = is_exit_terminal_synced and is_exit_image_synced
        users_qs = users_qs.annotate(
            enter_terminal_synced=models.Case(
                models.When(
                    models.Q(is_enter_terminal_synced=True, is_enter_image_synced=True),
                    then=True,
                ),
                default=False,
                output_field=models.BooleanField(),
            ),
            exit_terminal_synced=models.Case(
                models.When(
                    models.Q(is_exit_terminal_synced=True, is_exit_image_synced=True),
                    then=True,
                ),
                default=False,
                output_field=models.BooleanField(),
            ),
        )

        return users_qs

    @swagger_auto_schema(manual_parameters=USER_MANAGEMENT_FILTER_PARAMETERS)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


__all__ = ["UserListAPIView"]
