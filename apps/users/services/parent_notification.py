import time

import requests
from django.db.models import Q
from django.utils import dateformat, timezone
from django.utils.translation import gettext as _

from apps.common.services.logging import TelegramLogging
from apps.common.services.telegram import (send_telegram_message,
                                           send_telegram_message_image)
from apps.users.choices import FaceIDLogTypes


class ParentNotification:
    """
    This class is responsible for sending notification to parent when a child is detected in the school.
    Notification will be sent via TelegramTelegram
    ""
    """

    def __init__(self, bot_token, face_id_log):
        self.bot_token = bot_token
        self.face_id_log = face_id_log

    def generate_notification_message(self):
        # Generate notification message
        if self.face_id_log.type == FaceIDLogTypes.ENTER:
            msg = str(_("<b>🏫🤝 Sizning farzandingiz muassasamizga kirdi!</b> \n\n"))
        elif self.face_id_log.type == FaceIDLogTypes.EXIT:
            msg = str(_("<b>🏡👋🏻 Sizning farzandingiz muassasamizdan chiqdi!</b> \n\n"))
        msg += str(_("<i>🧑🏻‍🏫 Ismi</i>:  <b>{student_name}</b>\n" "<i>🕖 Vaqt</i>:  <b>{time}</b>"))

        logged_time = self.face_id_log.time
        logged_time_aware = logged_time.astimezone(timezone.get_current_timezone())
        # format time like: 31/01 12:30
        formatted_time = dateformat.format(logged_time_aware, "d/m • H:i")

        msg = msg.format(student_name=self.face_id_log.user.generate_full_name(), time=formatted_time)
        return msg

    def send_notification(self, tg_chat_id, for_teacher=False):
        face_log = self.face_id_log

        msg = self.generate_notification_message()
        if face_log.image:
            # send image with message
            status, res = send_telegram_message_image(self.bot_token, tg_chat_id, face_log.image.path, msg)
        else:
            status, res = send_telegram_message(self.bot_token, tg_chat_id, msg)

        if status is True:
            face_log.notification_log = res
            if for_teacher:
                face_log.is_notified_teacher = True
                face_log.save(update_fields=["is_notified_teacher", "notification_log"])
            else:
                face_log.is_notified = True
                face_log.save(update_fields=["is_notified", "notification_log"])

            return

        face_log.notification_log = res
        face_log.save(update_fields=["notification_log"])

    def _send_notification_to_parents(self):
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

    def send_notification_to_parents(self):
        try:
            self._send_notification_to_parents()
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            tg_logger = TelegramLogging(e)
            tg_logger.send_log_to_admin()

    def _send_notification_to_teachers(self):
        # Check if already notified or not
        if self.has_already_notified_duplicate_logging(for_teacher=True):
            return

        # Send notification to teachers
        educating_group = self.face_id_log.user.educating_group
        if not educating_group:
            return

        if not educating_group.teachers_tg_ids:
            return

        for teacher_tg_id in educating_group.teachers_tg_ids:
            self.send_notification(teacher_tg_id, for_teacher=True)
            # wait for some time before sending next notification via telegram
            time.sleep(0.1)

    def send_notification_to_teachers(self):
        try:
            self._send_notification_to_teachers()
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            tg_logger = TelegramLogging(e)
            tg_logger.send_log_to_admin()

    def has_already_notified_duplicate_logging(self, for_teacher=False):
        face_log = self.face_id_log

        from apps.users.models import FaceIDLog

        lower_bound = face_log.time - timezone.timedelta(minutes=2)
        upper_bound = face_log.time + timezone.timedelta(minutes=2)

        filter_query = Q(time__range=(lower_bound, upper_bound), user_id=face_log.user_id, type=face_log.type)

        if for_teacher:
            filter_query &= Q(is_notified_teacher=True)
        else:
            filter_query &= Q(is_notified=True)

        if FaceIDLog.objects.filter(filter_query).exists():
            return True

        return False
