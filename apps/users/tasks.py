from celery import shared_task
from django.utils import timezone

from apps.common.models import FaceIDSettings
from apps.users.choices import FaceIDLogTypes
from apps.users.services.attendance import AttendanceService


@shared_task
def get_and_store_attendance_log():
    face_id_settings = FaceIDSettings.get_solo()
    has_changes = False

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
        has_changes = True

    if bool(
        face_id_settings.exit_device_ip
        and face_id_settings.exit_device_username
        and face_id_settings.exit_device_password
        and face_id_settings.exit_device_last_sync_time
    ):
        attendance_service = AttendanceService(
            ip_address=face_id_settings.exit_device_ip,
            username="admin",
            password="admin123",
            last_sync_time=face_id_settings.exit_device_last_sync_time,
            log_type=FaceIDLogTypes.EXIT,
        )
        attendance_service.store_attendance_log()
        face_id_settings.exit_last_run = timezone.now()
        has_changes = True

    if has_changes:
        face_id_settings.save()
