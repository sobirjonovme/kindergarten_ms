from rest_framework.generics import CreateAPIView

from apps.accounting.models import MonthlyPayment
from apps.users.permissions import IsAdminUser

from .serializers import MonthlyPaymentCreateSerializer


class CreateMonthlyPaymentAPIView(CreateAPIView):
    """
    API endpoint to create payment of TUITION FEES and SALARIES
    type description:
    - TUITION_FEE  ->  for students tuition fees
    - SALARY  ->  for workers salaries
    """

    queryset = MonthlyPayment.objects.all()
    serializer_class = MonthlyPaymentCreateSerializer

    permission_classes = (IsAdminUser,)


__all__ = ["CreateMonthlyPaymentAPIView"]
