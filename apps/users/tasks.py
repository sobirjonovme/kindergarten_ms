from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.translation import activate

from apps.accounting.services.salary_calculation import WorkerSalaryCalculation
from apps.common.models import FaceIDSettings
from apps.common.services.logging import TelegramLogging
from apps.organizations.models import WorkingHourSettings
from apps.users.choices import FaceIDLogTypes, UserTypes
from apps.users.models import FaceIDLog, User
from apps.users.services.attendance import AttendanceService
from apps.users.services.daily_presence import (UserDailyPresence,
                                                recalculate_user_old_presences)
from apps.users.services.hikvision_user_info_sender import UserInfoSender
from apps.users.services.parent_notification import ParentNotification


@shared_task
def get_and_store_attendance_log():
    face_id_settings = FaceIDSettings.get_solo()

    if bool(
        face_id_settings.enter_device_ip
        and face_id_settings.enter_device_username
        and face_id_settings.enter_device_password
        and face_id_settings.enter_device_last_sync_time
    ):
        attendance_service = AttendanceService(
            ip_address=face_id_settings.enter_device_ip,
            username=face_id_settings.enter_device_username,
            password=face_id_settings.enter_device_password,
            last_sync_time=face_id_settings.enter_device_last_sync_time,
            log_type=FaceIDLogTypes.ENTER,
        )
        attendance_service.store_attendance_log()
        face_id_settings.enter_last_run = timezone.now()
        face_id_settings.save(update_fields=["enter_last_run"])

    if bool(
        face_id_settings.exit_device_ip
        and face_id_settings.exit_device_username
        and face_id_settings.exit_device_password
        and face_id_settings.exit_device_last_sync_time
    ):
        attendance_service = AttendanceService(
            ip_address=face_id_settings.exit_device_ip,
            username=face_id_settings.exit_device_username,
            password=face_id_settings.exit_device_password,
            last_sync_time=face_id_settings.exit_device_last_sync_time,
            log_type=FaceIDLogTypes.EXIT,
        )
        attendance_service.store_attendance_log()
        face_id_settings.exit_last_run = timezone.now()
        face_id_settings.save(update_fields=["exit_last_run"])


@shared_task
def send_face_id_notification_to_parents():
    bot_token = settings.BOT_TOKEN
    if not bot_token:
        return
    activate("uz")

    # today_beginning = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    lower_bound = timezone.now() - timezone.timedelta(minutes=60)
    face_id_logs = FaceIDLog.objects.filter(time__gte=lower_bound, is_notified=False).order_by("time")

    for face_id_log in face_id_logs:
        parent_notification = ParentNotification(bot_token=bot_token, face_id_log=face_id_log)
        parent_notification.send_notification_to_parents()


@shared_task
def send_user_info_to_hikvision(user_id):
    from apps.users.models import User

    user = User.objects.get(id=user_id)

    # check if the user has face_image
    if not user.face_image:
        return

    face_id_settings = FaceIDSettings.get_solo()

    if bool(
        face_id_settings.enter_device_ip
        and face_id_settings.enter_device_username
        and face_id_settings.enter_device_password
    ):
        user_info_sender = UserInfoSender(
            ip_address=face_id_settings.enter_device_ip,
            username=face_id_settings.enter_device_username,
            password=face_id_settings.enter_device_password,
            device_type=FaceIDLogTypes.ENTER,
            user_obj=user,
        )
        user_info_sender.send_user_data_to_hikvision()

    if bool(
        face_id_settings.exit_device_ip
        and face_id_settings.exit_device_username
        and face_id_settings.exit_device_password
    ):
        user_info_sender = UserInfoSender(
            ip_address=face_id_settings.exit_device_ip,
            username=face_id_settings.exit_device_username,
            password=face_id_settings.exit_device_password,
            device_type=FaceIDLogTypes.EXIT,
            user_obj=user,
        )
        user_info_sender.send_user_data_to_hikvision()


@shared_task
def calculate_and_story_users_presence_time(dates: list = None):
    working_hour_settings = WorkingHourSettings.get_solo()

    if dates:
        for target_date in dates:
            users = User.objects.all()
            for user in users:
                UserDailyPresence(user, target_date).store_daily_presence()

    # if dates is not provided,
    # calculate presence time for all days starting from the last calculation date to yesterday
    last_enter_log = FaceIDLog.objects.filter(type=FaceIDLogTypes.ENTER).order_by("-time").first()
    last_exit_log = FaceIDLog.objects.filter(type=FaceIDLogTypes.EXIT).order_by("-time").first()
    end_date = min(
        timezone.localtime(last_enter_log.time).date(),
        timezone.localtime(last_exit_log.time).date(),
    )
    start_date = working_hour_settings.last_calculation_date

    while start_date <= end_date:
        users = User.objects.all()
        for user in users:
            try:
                UserDailyPresence(user, start_date).store_daily_presence()
                if user.type in [UserTypes.TEACHER, UserTypes.EDUCATOR]:
                    recalculate_user_old_presences(user)
            except Exception as e:
                tg_logger = TelegramLogging(e)
                tg_logger.send_log_to_admin()

        start_date += timezone.timedelta(days=1)

    """
    Calculations for worker's working hours and salary
    """
    month_dates = [start_date]

    today = timezone.localdate()
    if start_date.month != today.month:
        month_dates.append(today)

    for month_date in month_dates:
        users = User.objects.filter(type__in=[UserTypes.TEACHER, UserTypes.EDUCATOR])
        for user in users:
            try:
                salary_calculator = WorkerSalaryCalculation(worker=user, month_date=month_date)
                salary_calculator.calculate()
            except Exception as e:
                tg_logger = TelegramLogging(e)
                tg_logger.send_log_to_admin()

    working_hour_settings.last_calculation_date = end_date
    working_hour_settings.save(update_fields=["last_calculation_date"])
