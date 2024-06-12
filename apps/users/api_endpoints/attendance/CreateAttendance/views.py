from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminUser

from .serializers import CreateAttendanceSerializer


class CreateAttendanceAPIView(APIView):
    serializer_class = CreateAttendanceSerializer
    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


__all__ = ["CreateAttendanceAPIView"]
