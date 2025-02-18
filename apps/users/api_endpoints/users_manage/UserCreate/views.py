from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView

from apps.users.models import User
from apps.users.permissions import IsAdminUser

from .serializers import UserCreateSerializer


class UserCreateAPIView(CreateAPIView):
    """
    <b>POST</b> request to create a new User.
    <h2> if type is student / kindergartener, request body example:</h2>
    <pre>
    <code>
        {
            "type": "student",
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "Caffrey o'g'li",
            "face_id": "97",
            "gender": "male",
            "tuition_fee": "string",
            "organization": 1,
            "educating_group": 1,
            "parents_tg_ids": [
                "12312412",
                "214124124"
            ]
        }
    <br></code>
    </pre>

    <h2> if type is teacher / educator / worker, request body example:</h2>
    <pre>
    <code>
        {
            "type": "teacher",
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "Caffrey o'g'li",
            "face_id": "97",
            "gender": "male",
            "work_start_time": "08:30:00",
            "work_end_time": "17:00:00",
            "salary": "150",
            "organization": 1,
            "parents_tg_ids": [
                "12312412",
                "214124124"
            ]
        }
    <br></code>
    </pre>
    """

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(tags=["User Management"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


__all__ = ["UserCreateAPIView"]
