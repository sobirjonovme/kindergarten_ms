from rest_framework import serializers

from apps.accounting.serializers import MonthlyPaymentListSerializer
from apps.users.models import User


class UserYearlyPaymentListSerializer(serializers.ModelSerializer):
    monthly_payments = serializers.SerializerMethodField()

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
        ref_name = "UserYearlyPaymentListSerializer"

    def get_monthly_payments(self, obj):
        return MonthlyPaymentListSerializer(self.context.get("payments"), many=True).data
