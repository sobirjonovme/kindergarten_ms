from rest_framework import serializers

from apps.accounting.models import MonthlyPayment
from apps.users.models import User


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


class UsersMonthlyPaymentListSerializer(serializers.ModelSerializer):
    monthly_payments = MonthlyPaymentListSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "type",
            "monthly_payments",
        )
        ref_name = "UsersMonthlyPaymentListSerializer"
