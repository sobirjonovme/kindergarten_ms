from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView

from apps.users.models import User
from apps.users.permissions import IsAdminUser

from .serializers import UserDetailSerializer


class UserDetailAPIView(RetrieveAPIView):
    """
    <b>GET</b> request to get a user details.
    <h2> if type is student / kindergartener, necessary response body fields:</h2>
    <pre>
    <code>
        {
            "type": "student",
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "Caffrey o'g'li",
            "face_image": "image_url",
            "face_id": "97",
            "gender": "male",
            "tuition_fee": "string",
            "organization": {
                "id": 1,
                "name": "Bog'cha"
            },
            "educating_group": {
                "id": 1,
                "name": "O'zbek tili o'rta guruh"
            },
            "parents_tg_ids": [
                "12312412",
                "214124124"
            ]
        }
    <br></code>
    </pre>

    <h2> if type is teacher / educator / worker, necessary response body fields:</h2>
    <pre>
    <code>
        {
            "type": "teacher",
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "Caffrey o'g'li",
            "face_image": "image_url",
            "face_id": "97",
            "gender": "male",
            "work_start_time": "08:30:00",
            "work_end_time": "17:00:00",
            "salary": "150",
            "organization": {
                "id": 1,
                "name": "Bog'cha"
            },
            "parents_tg_ids": [
                "12312412",
                "214124124"
            ]
        }
    <br></code>
    </pre>
    """

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(tags=["User Management"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


__all__ = ["UserDetailAPIView"]
