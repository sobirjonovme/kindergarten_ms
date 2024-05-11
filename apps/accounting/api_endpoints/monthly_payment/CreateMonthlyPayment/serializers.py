from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from apps.accounting.models import MonthlyPayment


class MonthlyPaymentCreateSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(
        write_only=True, required=True, allow_null=False, validators=[MinValueValidator(2020)]
    )
    month = serializers.IntegerField(
        write_only=True, required=True, allow_null=False, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    class Meta:
        model = MonthlyPayment
        fields = (
            "id",
            "type",
            "amount",
            "year",
            "month",
            "is_completed",
            "comment",
        )

    def create(self, validated_data):
        year = validated_data.pop("year")
        month = validated_data.pop("month")
        validated_data["paid_month"] = f"{year}-{month}-01"

        payment = MonthlyPayment(**validated_data)
        payment.save()

        return payment
