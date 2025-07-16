from .base_logger import BaseLogger
import requests
import re

class SlackLogger(BaseLogger):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def log(self, message: str, level: str = 'INFO'):
        # Replace []() with Slack-style links
        message = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', message)
        payload = {'text': f'[{level}] {message}'}
        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f'Failed to send Slack log: {e}')
