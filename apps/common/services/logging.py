import traceback

from apps.common.services.telegram import send_telegram_message


class LoggingException(Exception):
    def __init__(self, message, extra_kwargs: dict = None):
        self.message = message
        self.extra_kwargs = extra_kwargs
        super().__init__(self.message)


class TelegramLogging:
    def __init__(self, exception):
        self.bot_token = "6752870492:AAE6W4dA32_XULSu6okn1DIhp73GF8a7kgA"  # https://t.me/my_xp_logging_bot
        self.chat_id = "-1002103996575"
        self.exception = exception

    def send_log_to_admin(self):
        # Send the exception details to the admin
        extra = getattr(self.exception, "extra_kwargs", None)

        try:
            tb_list = traceback.format_exception(None, self.exception, self.exception.__traceback__)
            tb_string = "".join(tb_list)
            tb_string = tb_string.replace("<", "{")
            tb_string = tb_string.replace(">", "}")

            msg = "<b>ERROR | Kindergarten MS</b>\n\n"
            if extra:
                for key, value in extra.items():
                    msg += f"{key}: {value}\n"
            msg += f"\n<code>{tb_string[-4000 + len(msg):]}</code>"
            send_telegram_message(self.bot_token, self.chat_id, msg)
        except Exception as e:
            print(e)
