import urllib3
from django.core.management.base import BaseCommand

from apps.common.models import FaceIDSettings
from apps.users.services.hikvision_user_info_receiver import UserInfoReceiver

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        face_id_settings = FaceIDSettings.get_solo()

        if bool(
            face_id_settings.enter_device_ip
            and face_id_settings.enter_device_username
            and face_id_settings.enter_device_password
        ):
            user_info_receiver = UserInfoReceiver(
                ip_address=face_id_settings.enter_device_ip,
                username=face_id_settings.enter_device_username,
                password=face_id_settings.enter_device_password,
            )
            user_info_receiver.store_user_info_bulk()
