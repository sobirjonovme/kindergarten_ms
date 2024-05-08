from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from apps.users.filters import ATTENDANCE_FILTER_PARAMETERS, UserFilter
from apps.users.models import FaceIDLog, User

from .serializers import AttendanceListSerializer, DateSerializer


class AttendanceListAPIView(ListAPIView):
    serializer_class = AttendanceListSerializer

    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter

    def get_queryset(self):
        users_qs = User.objects.all()

        # check if date query parameter is present
        date_serializer = DateSerializer(data=self.request.query_params)
        date_serializer.is_valid(raise_exception=True)
        date = date_serializer.validated_data["date"]
        # Add is_present field to each user
        face_id_logs = FaceIDLog.objects.filter(time__date=date)
        users_qs = users_qs.annotate(is_present=models.Exists(face_id_logs.filter(user=models.OuterRef("id"))))

        return users_qs

    @swagger_auto_schema(manual_parameters=ATTENDANCE_FILTER_PARAMETERS)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


__all__ = ["AttendanceListAPIView"]
