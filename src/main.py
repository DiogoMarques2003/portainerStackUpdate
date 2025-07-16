import argparse
import os
from utils.helpers import init_config
from core.portainer import Portainer
from core.read_config_file import ReadConfigFile
from errors.read_config_file_error import ReadConfigFileError
from errors.portainer_error import PortainerError

def main():
    parser = argparse.ArgumentParser(description="Portainer stack automatic update")
    parser.add_argument('--config', type=str, help='Path to config.yml file')
    parser.add_argument('--init-config', action='store_true', help='Generate default config.yml file')
    args = parser.parse_args()

    default_config_path = os.path.join(os.getcwd(), 'config.yml')
    config_path = args.config if args.config else default_config_path

    if args.init_config:
        init_config(config_path)
        return
    
    try:
        config, logger = ReadConfigFile(config_path).read()
    except ReadConfigFileError as e:
        print(e)
        return

    # Send initialization message
    logger.log("Configuration file read successfully, starting processing.")

    print(config)

if __name__ == '__main__':
    main()
