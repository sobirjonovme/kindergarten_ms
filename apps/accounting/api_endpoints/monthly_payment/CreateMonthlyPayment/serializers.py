from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounting.models import MonthlyPayment
from apps.accounting.tasks import send_tuition_fee_update_msg_to_parents


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
            "user",
            "type",
            "amount",
            "year",
            "month",
            "is_completed",
            "comment",
        )
        extra_kwargs = {
            "user": {"required": True, "allow_null": False},
        }

    def validate(self, attrs):
        year = attrs.get("year")
        month = attrs.get("month")
        user = attrs.get("user")

        if MonthlyPayment.objects.filter(user=user, paid_month__year=year, paid_month__month=month).exists():
            raise serializers.ValidationError(
                code="already_exists",
                detail={"monthly_payment": _("Monthly payment for this month already exists.")},
            )

        return attrs

    def create(self, validated_data):
        year = validated_data.pop("year")
        month = validated_data.pop("month")
        validated_data["paid_month"] = f"{year}-{month}-01"

        payment = MonthlyPayment(**validated_data)
        payment.save()

        print("Sending tuition fee update message to parents")
        send_tuition_fee_update_msg_to_parents.delay(payment.id)

        return payment
