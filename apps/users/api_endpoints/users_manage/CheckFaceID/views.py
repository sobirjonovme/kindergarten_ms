from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User

from .serializers import CheckFaceIDSerializer


class CheckFaceIDAPIView(APIView):
    """
    <h1>Check Face ID availability</h1>
    <h2> if new user is being created, then user_id should be null:</h2>
    <pre>
    <code>
        {
            "face_id": "999",
            "user_id": null
        }
    <br></code>
    </pre>

    <h2> if user is being updated, then user_id should be the id of the user being updated:</h2>
    <pre>
    <code>
        {
            "face_id": "999",
            "user_id": 999
        }
    <br></code>
    </pre>
    """

    @swagger_auto_schema(
        request_body=CheckFaceIDSerializer,
        tags=["User Management"],
    )
    def post(self, request):
        serializer = CheckFaceIDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        face_id = serializer.validated_data.get("face_id")
        user_id = serializer.validated_data.get("user_id")

        if user_id is not None:
            get_object_or_404(User, id=user_id)

        # check if given FaceID number is available in the database
        if User.objects.filter(face_id=face_id).exclude(id=user_id).exists():
            return Response(
                {"message": "Face ID is NOT available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Face ID is available"},
            status=status.HTTP_200_OK,
        )


__all__ = ["CheckFaceIDAPIView"]
