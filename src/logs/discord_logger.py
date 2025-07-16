from .base_logger import BaseLogger
import requests

class DiscordLogger(BaseLogger):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def log(self, message: str, level: str = "INFO"):
        payload = {"content": f"[{level}] {message}"}
        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f"Failed to send Discord log: {e}")
