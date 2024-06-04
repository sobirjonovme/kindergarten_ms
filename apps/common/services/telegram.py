import typing

from telegram import Bot


def send_telegram_message(bot_token, chat_id, text) -> typing.Tuple[bool, typing.Union[dict, str, Exception]]:
    bot = Bot(token=bot_token)
    try:
        msg = bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")

        return True, msg.result

    except Exception as e:  # noqa
        print(e)
        return False, e
