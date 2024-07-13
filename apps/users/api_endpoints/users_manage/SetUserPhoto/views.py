from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import MultiPartParser

from apps.users.models import User
from apps.users.permissions import IsAdminUser

from .serializers import SetUserPhotoSerializer


class SetUserPhotoAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = SetUserPhotoSerializer
    permission_classes = (IsAdminUser,)

    parser_classes = (MultiPartParser,)
    http_method_names = ["put"]


__all__ = ["SetUserPhotoAPIView"]
