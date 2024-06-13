from rest_framework import serializers

from apps.accounting.models import MonthlyPayment
from apps.accounting.tasks import send_tuition_fee_update_msg_to_parents


class UpdatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyPayment
        fields = (
            "id",
            "amount",
            "is_completed",
            "comment",
        )

    def save(self, **kwargs):
        payment = super().save(**kwargs)
        send_tuition_fee_update_msg_to_parents.delay(payment.id)
        return payment
