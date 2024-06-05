import time

from django.utils import dateformat, timezone
from django.utils.translation import gettext as _

from apps.common.services.telegram import (send_telegram_message,
                                           send_telegram_message_image)
from apps.users.choices import FaceIDLogTypes


class ParentNotification:
    """
    This class is responsible for sending notification to parent when a child is detected in the school.
    Notification will be sent via TelegramTelegram
    ""
    """

    def __init__(self, face_id_log):
        self.face_id_log = face_id_log
        self.bot_token = "5060653181:AAGYXXcL4VvPLXuc8cz2Ec9AHgG6fMUjsRg"

    def generate_notification_message(self):
        # Generate notification message
        if self.face_id_log.type == FaceIDLogTypes.ENTER:
            msg = str(_("<b>🏫🤝 Sizning farzandingiz muassasamizga yetib keldi!</b> \n\n"))
        elif self.face_id_log.type == FaceIDLogTypes.EXIT:
            msg = str(_("<b>🏡👋🏻 Sizning farzandingiz muassasamizni tark etdi!</b> \n\n"))
        msg += str(_("<i>🧑🏻‍🏫 Ismi</i>:  <b>{student_name}</b>\n" "<i>🕖 Vaqt</i>:  <b>{time}</b>"))

        logged_time = self.face_id_log.time
        logged_time_aware = logged_time.astimezone(timezone.get_current_timezone())
        # format time like: 31/01 12:30
        formatted_time = dateformat.format(logged_time_aware, "d/m • H:i")

        msg = msg.format(student_name=self.face_id_log.user.generate_full_name(), time=formatted_time)
        return msg

    def send_notification(self, tg_chat_id):
        face_log = self.face_id_log
        user = face_log.user

        msg = self.generate_notification_message()
        if user.face_image:
            # send image with message
            status, res = send_telegram_message_image(self.bot_token, tg_chat_id, user.face_image.path, msg)
        else:
            status, res = send_telegram_message(self.bot_token, tg_chat_id, msg)

        if face_log.is_notified is True:
            # it is enough to send notification to one parent
            # even if there are multiple parents and another parent notification is not sent
            # so NO NEED to save notification log
            return

        if status is True:
            face_log.is_notified = True
            face_log.notification_log = res
            face_log.save(update_fields=["is_notified", "notification_log"])
            return

        face_log.notification_log = res
        face_log.save(update_fields=["notification_log"])

    def send_notification_to_parents(self):
        # Check if already notified or not
        if self.has_already_notified_duplicate_logging():
            return

        # Send notification to parent
        parents_tg_ids = self.face_id_log.user.parents_tg_ids
        if not parents_tg_ids:
            return

        for parent_tg_id in parents_tg_ids:
            self.send_notification(parent_tg_id)
            # wait for some time before sending next notification via telegram
            time.sleep(0.1)

    def has_already_notified_duplicate_logging(self):
        face_log = self.face_id_log

        from apps.users.models import FaceIDLog

        lower_bound = face_log.time - timezone.timedelta(minutes=2)
        upper_bound = face_log.time + timezone.timedelta(minutes=2)

        if (
            FaceIDLog.objects.filter(
                time__range=(lower_bound, upper_bound), user_id=face_log.user_id, is_notified=True, type=face_log.type
            )
            .exclude(id=face_log.id)
            .exists()
        ):
            return True

        return False
