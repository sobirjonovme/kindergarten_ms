from rest_framework import serializers

from apps.accounting.models import Expense, ExpenseType, MonthlyPayment


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
            # salary calculation fields for WORKERS
            "present_days",
            "worked_hours",
            "total_working_days",
            "calculated_salary",
        )
        ref_name = "MonthlyPaymentListSerializer"


class ExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        fields = (
            "id",
            "name",
        )


class ExpenseListSerializer(serializers.ModelSerializer):
    type = ExpenseTypeSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = (
            "id",
            "type",
            "amount",
            "date",
            "comment",
        )
