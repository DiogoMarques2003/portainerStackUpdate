from .base_logger import BaseLogger
import requests

class TelegramLogger(BaseLogger):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    def log(self, message: str, level: str = 'INFO'):
        text = f'[{level}] {message}'
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'markdown'
        }
        try:
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()
        except Exception as e:
            print(f'Failed to send Telegram log: {e}')

