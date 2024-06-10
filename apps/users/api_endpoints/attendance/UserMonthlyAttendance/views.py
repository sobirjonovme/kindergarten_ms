from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import FaceIDLog, User
from apps.users.permissions import IsAdminUser
from apps.users.serializers import UserShortSerializer

from .serializers import YearMonthSerializer

FILTER_PARAMETERS = [
    openapi.Parameter("year", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
    openapi.Parameter("month", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
]


class UserMonthlyAttendanceAPIView(APIView):
    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(manual_parameters=FILTER_PARAMETERS)
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        serializer = YearMonthSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        year = serializer.validated_data["year"]
        month = serializer.validated_data["month"]

        face_id_logs = FaceIDLog.objects.filter(user=user, time__year=year, time__month=month)
        attendance_days = face_id_logs.values_list("time__day", flat=True).distinct()

        data = {
            "year": year,
            "month": month,
            "user": UserShortSerializer(user, context={"request": request}).data,
            "total_attended_days": len(attendance_days),
            "attended_days": list(attendance_days),
        }
        return Response(data=data, status=status.HTTP_200_OK)


__all__ = ["UserMonthlyAttendanceAPIView"]
