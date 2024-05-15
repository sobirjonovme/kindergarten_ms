from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

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

    # custom attribute to store the total payment
    total_payment = 0

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related("type")
        qs = qs.order_by("-date")

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # calculate total amount of payment
        self.total_payment = queryset.aggregate(total_payment=models.Sum("amount"))["total_payment"]

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)

        if isinstance(res.data, list):
            res.data = {
                "total_payment": self.total_payment,
                "data": res.data,
            }
        elif isinstance(res.data, dict):
            res.data = {"total_payment": self.total_payment, **res.data}

        return res


__all__ = ["ExpenseListAPIView"]
