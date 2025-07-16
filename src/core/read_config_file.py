from yaml import safe_load
from errors.read_config_file_error import ReadConfigFileError
from logs.console_logger import ConsoleLogger
from logs.discord_logger import DiscordLogger
from logs.slack_logger import SlackLogger
from logs.telegram_logger import TelegramLogger

class ReadConfigFile:
    def __init__(self, path: str):
        self.path = path

    def _init_logger(self, logging_config: dict):
        '''Initialize the logger based on the provided configuration.'''
        logger_type = logging_config.get('type', 'console').lower()

        if logger_type == 'console':
            return ConsoleLogger()
        
        if logger_type == 'discord':
            webhook_url = logging_config.get('webhookUrl')
            if not webhook_url:
                raise ReadConfigFileError('Discord logger requires a "webhookUrl" in the configuration.')
            return DiscordLogger(webhook_url)
        
        if logger_type == 'slack':
            webhook_url = logging_config.get('webhookUrl')
            if not webhook_url:
                raise ReadConfigFileError('Slack logger requires a "webhookUrl" in the configuration.')
            return SlackLogger(webhook_url)
        
        if logger_type == 'telegram':
            bot_token = logging_config.get('botToken')
            chat_id = logging_config.get('chatId')
            if not bot_token or not chat_id:
                raise ReadConfigFileError('Telegram logger requires "botToken" and "chatId" in the configuration.')
            return TelegramLogger(bot_token, chat_id)

    def read(self):
        '''Read the configuration file and return the contents.'''
        try:
            with open(self.path, 'r') as file:
                config = safe_load(file)

            if not config or not isinstance(config, dict):
                raise ReadConfigFileError('Configuration file is empty or invalid.')
            
            if not config.get('instances') or not isinstance(config.get('instances'), list):
                raise ReadConfigFileError('No instances found in the configuration file.')
            
            logging_config = config.get('logging', {})
            logger = self._init_logger(logging_config)

            return config, logger
        except FileNotFoundError:
            raise ReadConfigFileError(f'Configuration file not found at {self.path}. Please provide a valid path or use --init-config to create a default one.')
        except Exception as e:
            if isinstance(e, ReadConfigFileError):
                raise e
            raise ReadConfigFileError(f'An error occurred while reading the configuration file: {e}')