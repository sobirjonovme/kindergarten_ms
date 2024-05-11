from rest_framework import serializers

from apps.accounting.models import MonthlyPayment


class UpdatePaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyPayment
        fields = (
            "id",
            "amount",
            "is_completed",
            "comment",
        )
