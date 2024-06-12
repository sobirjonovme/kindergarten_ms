from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounting.models import MonthlyPayment
from apps.common.services.logging import TelegramLogging
from apps.common.services.telegram import send_telegram_message
from apps.users.choices import UserTypes
from apps.users.models import User


class TuitionFeeNotificationService:
    def __init__(self):
        self.bot_token = settings.BOT_TOKEN

    def send_child_tuition_fee_warning(self, child):
        parent_tg_ids = child.parents_tg_ids
        if not parent_tg_ids:
            return

        msg = str(
            _(
                "Xurmatli ota-ona! "
                "Farzandingiz, {child_name}, uchun oylik to'lovni amalga oshirish muddati o'tib ketganligini ma'lum qilamiz"
                "Iltimos, to'lovni amalga oshiring"
            )
        ).format(child_name=child.generate_full_name())

        for tg_chat_id in parent_tg_ids:
            send_telegram_message(self.bot_token, tg_chat_id, msg)

    def send_tuition_fee_notification_to_parents(self):
        """Send notification to parents about tuition fee."""
        # Get all students who have not paid the tuition fee

        current_date = timezone.localdate()
        children = User.objects.filter(type__in=UserTypes.get_student_types())

        for child in children:
            try:
                payments = MonthlyPayment.objects.filter(
                    user=child, paid_month__year=current_date.year, paid_month__month=current_date.month
                )
                if not payments:
                    self.send_child_tuition_fee_warning(child)
            except Exception as e:
                tg_logger = TelegramLogging(e)
                tg_logger.send_log_to_admin()
