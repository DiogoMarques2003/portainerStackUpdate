from yaml import safe_load
from errors.read_config_file_error import ReadConfigFileError
from logs.console_logger import ConsoleLogger
from logs.discord_logger import DiscordLogger

class ReadConfigFile:
    def __init__(self, path: str):
        self.path = path

    def _init_logger(self, logging_config: dict):
        """Initialize the logger based on the provided configuration."""
        logger_type = logging_config.get('type', 'console').lower()

        if logger_type == 'console':
            return ConsoleLogger()
        
        if logger_type == 'discord':
            webhook_url = logging_config.get('webhook_url')
            if not webhook_url:
                raise ReadConfigFileError("Discord logger requires a 'webhook_url' in the configuration.")
            return DiscordLogger(webhook_url)

    def read(self):
        """Read the configuration file and return the contents."""
        try:
            with open(self.path, 'r') as file:
                config = safe_load(file)

            if not config or not isinstance(config, dict):
                raise ReadConfigFileError("Configuration file is empty or invalid.")
            
            if not config.get('instances'):
                raise ReadConfigFileError("No instances found in the configuration file.")
            
            logging_config = config.get('logging', {})
            logger = self._init_logger(logging_config)

            return config, logger
        except FileNotFoundError:
            raise ReadConfigFileError(f"Configuration file not found at {self.path}. Please provide a valid path or use --init-config to create a default one.")
        except Exception as e:
            raise ReadConfigFileError(f"An error occurred while reading the configuration file: {e}")