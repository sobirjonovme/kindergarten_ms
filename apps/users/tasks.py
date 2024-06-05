from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.translation import activate

from apps.common.models import FaceIDSettings
from apps.users.choices import FaceIDLogTypes
from apps.users.models import FaceIDLog
from apps.users.services.attendance import AttendanceService
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
