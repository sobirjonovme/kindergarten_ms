from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HelperAPIView(APIView):
    def get(self, request):

        return Response({"success": "OK"}, status=status.HTTP_200_OK)


__all__ = ["HelperAPIView"]
