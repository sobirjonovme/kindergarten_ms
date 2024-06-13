from celery import shared_task

from apps.accounting.choices import MonthlyPaymentTypes
from apps.accounting.models import MonthlyPayment
from apps.accounting.services.tuition_fee_notification import (
    TuitionFeeNotificationService, TuitionFeeUpdateService)


@shared_task
def send_tuition_fee_notification_warning_to_parents():
    notification_service = TuitionFeeNotificationService()
    notification_service.send_tuition_fee_notification_to_parents()


@shared_task
def send_tuition_fee_update_msg_to_parents(monthly_payment_id):
    monthly_payment = MonthlyPayment.objects.get(id=monthly_payment_id)

    if monthly_payment.type == MonthlyPaymentTypes.TUITION_FEE:
        update_service = TuitionFeeUpdateService(monthly_payment)
        update_service.send_child_tuition_fee_update_msg_to_parents()


@shared_task()
def check_unnotified_monthly_payments():
    monthly_payments = MonthlyPayment.objects.filter(is_notified=False)

    for monthly_payment in monthly_payments:
        if monthly_payment.type == MonthlyPaymentTypes.TUITION_FEE:
            update_service = TuitionFeeUpdateService(monthly_payment)
            update_service.send_child_tuition_fee_update_msg_to_parents()
