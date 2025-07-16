import sys
import os
import shutil
from core.portainer import Portainer
from logs.base_logger import BaseLogger

def resource_path(relative_path):
    '''Get absolute path to resource, works in dev and compiled versions.'''
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    return os.path.join(base_path, relative_path)

def init_config(target_path):
    '''Initialize the configuration file by copying the example configuration.'''
    example_path = resource_path(os.path.join('resources', 'example-config.yml'))

    if os.path.exists(target_path):
        print(f'The file "{target_path}" already exists. Please remove it before generating a new configuration.')
        return
    
    if not os.path.exists(example_path):
        print(f'Example file "{example_path}" not found.')
        return
    
    # Ensure the target directory exists
    target_dir = os.path.dirname(target_path)
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Copy the example configuration file to the target path    
    shutil.copyfile(example_path, target_path)
    print(f'Configuration file created at: {target_path}')

def delete_unused_images(portainer: Portainer, logger: BaseLogger, environment_id: int, environment_name: str, name: str, host: str):
    '''Function with logic to delete unused images in a specific environment.'''
    logger.log(f'Deleting unused images in environment [{environment_name}] of Portainer instance [{name}]({host}).')
    images = portainer.get_images_with_usage(environment_id)
    
    images_to_delete = [image for image in images if not image.get('used', True)]

    if not images_to_delete:
        logger.log(f'No unused images found in environment [{environment_name}] of Portainer instance [{name}]({host}).')
        return
    
    for image in images_to_delete:
        image_id = image.get('id')
        image_tags = image.get('tags', [])
        image_tag = image_tags[0] if image_tags else image_id

        if not image_id:
            logger.log(f'Image {image_tag} does not have a valid ID, skipping deletion.', level='WARNING')
            continue

        portainer.delete_image(environment_id, image_id)
        logger.log(f'Deleted unused image {image_tag} in environment [{environment_name}] of Portainer instance [{name}]({host}).')
    