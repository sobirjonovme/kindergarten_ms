from celery import shared_task

from apps.accounting.services.tuition_fee_notification import \
    TuitionFeeNotificationService


@shared_task
def send_tuition_fee_notification_warning_to_parents():
    notification_service = TuitionFeeNotificationService()
    notification_service.send_tuition_fee_notification_to_parents()
