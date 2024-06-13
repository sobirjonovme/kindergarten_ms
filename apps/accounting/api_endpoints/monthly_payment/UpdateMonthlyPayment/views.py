from rest_framework.generics import UpdateAPIView

from apps.accounting.models import MonthlyPayment
from apps.users.permissions import IsAdminUser

from .serializers import UpdatePaymentSerializer


class UpdateMonthlyPaymentAPIView(UpdateAPIView):
    queryset = MonthlyPayment.objects.all()
    serializer_class = UpdatePaymentSerializer

    permission_classes = (IsAdminUser,)


__all__ = ["UpdateMonthlyPaymentAPIView"]
