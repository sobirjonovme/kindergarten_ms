import requests


def send_telegram_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        response = requests.post(
            url=url,
            params={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        )
        return response.json()
    except Exception as e:  # noqa
        print(e)
        return e
