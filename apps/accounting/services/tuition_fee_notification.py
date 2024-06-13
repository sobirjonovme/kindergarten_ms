from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounting.models import MonthlyPayment
from apps.common.services.common import format_number_readable
from apps.common.services.logging import TelegramLogging
from apps.common.services.telegram import send_telegram_message
from apps.users.choices import UserTypes
from apps.users.models import User


class TuitionFeeNotificationService:
    def __init__(self):
        self.bot_token = settings.BOT_TOKEN

    def generate_notification_text(self, child):
        current_date = timezone.localdate()

        if current_date.day <= 5:
            txt = str(
                _(
                    "<b>Xurmatli ota-ona!</b> 👨‍👩‍👦\n"
                    "🧑🏻‍🏫 Farzandingiz, <i>{child_name}</i>, uchun yangi oyga to'lovni amalga oshirishingizni iltimos qilamiz.💸\n\n"
                    "🏫 <i>Xurmat bilan ma'muriyat!</i>"
                )
            ).format(child_name=child.generate_full_name())
            return txt

        txt = str(
            _(
                "<b>Xurmatli ota-ona!</b> 👨‍👩‍👦\n"
                "🧑🏻‍🏫 Farzandingiz, <i>{child_name}</i>, uchun oylik to'lovni amalga oshirish muddati o'tib ketganligini ma'lum qilamiz\n"
                "Iltimos, to'lovni amalga oshiring 💸\n\n"
                "🏫 <i>Xurmat bilan ma'muriyat!</i>"
            )
        ).format(child_name=child.generate_full_name())
        return txt

    def send_child_tuition_fee_warning(self, child):
        parent_tg_ids = child.parents_tg_ids
        if not parent_tg_ids:
            return

        msg = self.generate_notification_text(child)

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


class TuitionFeeUpdateService:
    def __init__(self, tuition_fee):
        self.bot_token = settings.BOT_TOKEN
        self.tuition_fee = tuition_fee

    def generate_notification_text(self):
        tuition_fee = self.tuition_fee
        child = tuition_fee.user

        # get payment month and year like 2024-06
        paid_month = tuition_fee.paid_month.strftime("%Y-%m")
        money_amount = tuition_fee.amount
        money_amount = format_number_readable(money_amount)

        txt = str(
            _(
                "<b>Xurmatli ota-ona!</b> 👨‍👩‍👦\n"
                "🧑🏻‍🏫 Farzandingiz, <i>{child_name}</i>ga {paid_month} oyi uchun qilgan to'lovingiz yangilandi\n"
                "💸 Umumiy summa:   {money_amount} so'm\n\n"
                "🏫 <i>Xurmat bilan ma'muriyat!</i>"
            )
        ).format(child_name=child.generate_full_name(), paid_month=paid_month, money_amount=money_amount)
        return txt

    def send_child_tuition_fee_update_msg_to_parents(self):
        try:
            parent_tg_ids = self.tuition_fee.user.parents_tg_ids
            if not parent_tg_ids:
                return

            txt = self.generate_notification_text()
            for tg_chat_id in parent_tg_ids:
                send_telegram_message(self.bot_token, tg_chat_id, txt)

            self.tuition_fee.is_notified = True
            self.tuition_fee.save(update_fields=["is_notified"])
        except Exception as e:
            tg_logger = TelegramLogging(e)
            tg_logger.send_log_to_admin()
