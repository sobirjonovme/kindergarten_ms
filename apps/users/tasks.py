from celery import shared_task
from django.utils import timezone
from django.utils.translation import activate

from apps.common.models import FaceIDSettings
from apps.users.choices import FaceIDLogTypes
from apps.users.models import FaceIDLog
from apps.users.services.attendance import AttendanceService
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
    activate("uz")
    # today_beginning = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    lower_bound = timezone.now() - timezone.timedelta(minutes=60)

    face_id_logs = FaceIDLog.objects.filter(time__gte=lower_bound, is_notified=False).order_by("time")

    for face_id_log in face_id_logs:
        parent_notification = ParentNotification(face_id_log)
        parent_notification.send_notification_to_parents()
