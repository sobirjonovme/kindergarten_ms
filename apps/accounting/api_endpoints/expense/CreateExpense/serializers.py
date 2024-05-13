from rest_framework import serializers

from apps.accounting.models import Expense


class CreateExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = (
            "id",
            "type",
            "amount",
            "comment",
        )
