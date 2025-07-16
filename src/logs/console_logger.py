from .base_logger import BaseLogger

class ConsoleLogger(BaseLogger):
    def log(self, message: str, level: str = 'INFO'):
        print(f'[{level}] {message}')
