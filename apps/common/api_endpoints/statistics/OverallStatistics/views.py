from django.db import models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.choices import UserTypes
from apps.users.models import User


class OverallStatisticsAPIView(APIView):
    def get(self, request):
        users_counts = User.objects.all().aggregate(
            school_studens=models.Count("id", filter=models.Q(type=UserTypes.STUDENT), distinct=True),
            teachers=models.Count("id", filter=models.Q(type=UserTypes.TEACHER), distinct=True),
            kindergarten_students=models.Count("id", filter=models.Q(type=UserTypes.KINDERGARTENER), distinct=True),
            kindergarten_educators=models.Count("id", filter=models.Q(type=UserTypes.EDUCATOR), distinct=True),
        )

        return Response(users_counts, status=status.HTTP_200_OK)


__all__ = ["OverallStatisticsAPIView"]
