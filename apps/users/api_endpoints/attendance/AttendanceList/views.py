from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from apps.users.filters import ATTENDANCE_FILTER_PARAMETERS, UserFilter
from apps.users.models import FaceIDLog, User
from apps.users.permissions import IsAdminUser

from .serializers import AttendanceListSerializer, DateSerializer


class AttendanceListAPIView(ListAPIView):
    serializer_class = AttendanceListSerializer
    pagination_class = None
    permission_classes = (IsAdminUser,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter

    # custom attribute to store the total amount of present users
    total_users = 0
    total_present_users = 0

    def get_queryset(self):
        users_qs = User.objects.all()

        # check if date query parameter is present
        date_serializer = DateSerializer(data=self.request.query_params)
        date_serializer.is_valid(raise_exception=True)
        date = date_serializer.validated_data["date"]
        # Add is_present field to each user
        face_id_logs = FaceIDLog.objects.filter(time__date=date)
        users_qs = users_qs.annotate(is_present=models.Exists(face_id_logs.filter(user=models.OuterRef("id"))))

        # calculate the total amount of present users
        self.total_users = users_qs.count()
        self.total_present_users = users_qs.filter(is_present=True).count()

        return users_qs

    @swagger_auto_schema(manual_parameters=ATTENDANCE_FILTER_PARAMETERS)
    def get(self, request, *args, **kwargs):
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
