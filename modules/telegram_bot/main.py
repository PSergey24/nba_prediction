import requests
import json
from setting import TELEGRAM_CHAT_ID, TELEGRAM_BOT_TOKEN


class TelegramBot:

    @staticmethod
    def send_message(message):
        params = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.get(url, params=params)
        if r.status_code == 200:
            return True
        else:
            r.raise_for_status()
