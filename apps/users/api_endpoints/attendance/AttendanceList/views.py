from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from apps.users.filters import ATTENDANCE_FILTER_PARAMETERS, UserFilter
from apps.users.models import User, UserPresence
from apps.users.permissions import IsAdminUser

from .serializers import AttendanceListSerializer, DateSerializer


class AttendanceListAPIView(ListAPIView):
    serializer_class = AttendanceListSerializer
    # pagination_class = None
    permission_classes = (IsAdminUser,)

    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = UserFilter
    search_fields = ("first_name", "last_name", "middle_name")

    # custom attribute to store the total amount of present users
    total_users = 0
    total_present_users = 0

    def get_queryset(self):
        users_qs = User.objects.order_by("first_name", "last_name", "middle_name")

        # get date query parameter
        date = self.request.query_params.get("date")
        # Add is_present field to each user
        user_presences = UserPresence.objects.filter(date=date)
        # face_id_logs = FaceIDLog.objects.filter(time__date=date)
        users_qs = users_qs.annotate(is_present=models.Exists(user_presences.filter(user=models.OuterRef("id"))))

        return users_qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # calculate the total amount of present users
        self.total_users = queryset.count()
        self.total_present_users = queryset.filter(is_present=True).count()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=ATTENDANCE_FILTER_PARAMETERS)
    def get(self, request, *args, **kwargs):
        # check if date query parameter is present and valid
        date_serializer = DateSerializer(data=self.request.query_params)
        date_serializer.is_valid(raise_exception=True)

        res = super().get(request, *args, **kwargs)

        if isinstance(res.data, list):
            res.data = {
                "total_users": self.total_users,
                "total_present_users": self.total_present_users,
                "data": res.data,
            }
        elif isinstance(res.data, dict):
            res.data = {"total_presences": self.total_present_users, **res.data}

        return res


__all__ = ["AttendanceListAPIView"]
