from rest_framework.generics import ListAPIView

from apps.accounting.models import ExpenseType
from apps.accounting.serializers import ExpenseTypeSerializer


class ExpenseTypeListAPIView(ListAPIView):
    queryset = ExpenseType.objects.all()
    serializer_class = ExpenseTypeSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by("name")
        return qs


__all__ = ["ExpenseTypeListAPIView"]
