from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView

from apps.accounting.filters import YEAR_FILTER_PARAMETERS, YearFilter
from apps.users.models import User
from apps.users.permissions import IsAdminUser

from .serializers import UserYearlyPaymentListSerializer


class UserYearlyPaymentListAPIView(APIView):
    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(manual_parameters=YEAR_FILTER_PARAMETERS)
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get("user_id"))

        # check if YEAR parameter is in the request query params
        year = request.query_params.get("year")
        if not year:
            raise ValidationError(
                code="required",
                detail={"year": "Year is required in the query parameters."},
            )

        payments = YearFilter(request.query_params, queryset=user.monthly_payments).qs

        serializer = UserYearlyPaymentListSerializer(user, context={"request": request, "payments": payments})
        return Response(serializer.data, status=status.HTTP_200_OK)


__all__ = ["UserYearlyPaymentListAPIView"]
