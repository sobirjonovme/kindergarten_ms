from rest_framework import serializers

from apps.accounting.models import MonthlyPayment


class MonthlyPaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyPayment
        fields = (
            "id",
            "type",
            "amount",
            "paid_month",
            "is_completed",
            "comment",
        )
        ref_name = "MonthlyPaymentListSerializer"
