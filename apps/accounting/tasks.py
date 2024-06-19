from celery import shared_task

from apps.accounting.choices import MonthlyPaymentTypes
from apps.accounting.models import MonthlyPayment
from apps.accounting.services.salary_calculation import WorkerSalaryCalculation
from apps.accounting.services.tuition_fee_notification import (
    TuitionFeeNotificationService, TuitionFeeUpdateService)
from apps.common.services.logging import TelegramLogging
from apps.users.choices import UserTypes
from apps.users.models import User


@shared_task
def send_tuition_fee_notification_warning_to_parents():
    """
    Notifications to warn the parents who did not pay tuition fee yet
    """
    notification_service = TuitionFeeNotificationService()
    notification_service.send_tuition_fee_notification_to_parents()


@shared_task
def send_tuition_fee_update_msg_to_parents(monthly_payment_id):
    """
    Notify parents about their tuition fee created or updated in our system
    """
    monthly_payment = MonthlyPayment.objects.get(id=monthly_payment_id)

    if monthly_payment.type == MonthlyPaymentTypes.TUITION_FEE:
        update_service = TuitionFeeUpdateService(monthly_payment)
        update_service.send_child_tuition_fee_update_msg_to_parents()


@shared_task
def check_unnotified_monthly_payments():
    """
    Check monthly payment objects and send update notifications if not already sent
    """
    monthly_payments = MonthlyPayment.objects.filter(is_notified=False)

    for monthly_payment in monthly_payments:
        if monthly_payment.type == MonthlyPaymentTypes.TUITION_FEE:
            update_service = TuitionFeeUpdateService(monthly_payment)
            update_service.send_child_tuition_fee_update_msg_to_parents()


@shared_task
def calculate_workers_salaries(month_date):
    users = User.objects.filter(type__in=[UserTypes.TEACHER, UserTypes.EDUCATOR])
    for user in users:
        try:
            salary_calculator = WorkerSalaryCalculation(worker=user, month_date=month_date)
            salary_calculator.calculate()
        except Exception as e:
            tg_logger = TelegramLogging(e)
            tg_logger.send_log_to_admin()


@shared_task
def calculate_salary(user_id, month_date):
    user = User.objects.get(id=user_id)
    salary_calculator = WorkerSalaryCalculation(worker=user, month_date=month_date)
    salary_calculator.calculate()
