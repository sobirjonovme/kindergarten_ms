from rest_framework.generics import CreateAPIView

from apps.accounting.models import Expense
from apps.users.permissions import IsAdminUser

from .serializers import CreateExpenseSerializer


class CreateExpenseViewAPIView(CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = CreateExpenseSerializer

    permission_classes = (IsAdminUser,)


__all__ = ["CreateExpenseViewAPIView"]
