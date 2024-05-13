from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from apps.accounting.filters import ExpenseFilter
from apps.accounting.models import Expense
from apps.accounting.serializers import ExpenseListSerializer
from apps.users.permissions import IsAdminUser


class ExpenseListAPIView(ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseListSerializer

    permission_classes = (IsAdminUser,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpenseFilter

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related("type")
        qs = qs.order_by("-date")
        return qs


__all__ = ["ExpenseListAPIView"]
