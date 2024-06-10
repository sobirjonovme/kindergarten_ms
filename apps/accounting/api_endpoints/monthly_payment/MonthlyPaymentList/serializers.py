from rest_framework import serializers

from apps.accounting.serializers import MonthlyPaymentListSerializer
from apps.users.models import User


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
            "face_image",
            "monthly_payments",
        )
        ref_name = "UsersMonthlyPaymentListSerializer"
