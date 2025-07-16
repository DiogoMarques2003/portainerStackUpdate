import argparse
import os
import time
from utils.helpers import init_config, delete_unused_images
from core.portainer import Portainer
from core.read_config_file import ReadConfigFile
from errors.read_config_file_error import ReadConfigFileError
from errors.portainer_error import PortainerError

def main():
    parser = argparse.ArgumentParser(description='Portainer stack automatic update')
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
    logger.log('Configuration file loaded successfully, starting processing.')
    any_stack_updated = False

    # Process each Portainer instance and perform actions
    for index, instance in enumerate(config.get('instances', [])):
        name = instance.get('name')
        host = instance.get('host')
        access_token = instance.get('accessToken')
        verify_ssl = instance.get('verifySSL', False)
        update_portainer = instance.get('updatePortainerVersion', False)
        delete_unused_images_flag = instance.get('deleteUnusedImages', False)
        purne_services = instance.get('purneServices', False)
        ignore_stack = instance.get('ignoreStacks', [])
        update_stacks_with_git = instance.get('updateStacksWithGitIntegration', False)

        if not all([name, host, access_token]):
            logger.log(f'Instance {name} is missing required fields.' if name else
                       f'Instance at index {index} is missing required fields.',
                       level='ERROR')
            continue

        portainer = Portainer(url=host, access_token=access_token, verify_ssl=verify_ssl)

        try:
            # Ping the Portainer instance
            portainer.ping()
            logger.log(f'Successfully connected to Portainer instance: [{name}]({host})')

            # Check if Portainer needs an update
            if update_portainer and portainer.check_if_portainer_needs_update():
                logger.log(f'Portainer instance [{name}]({host}) needs an update.')
                if portainer.update_portainer_version():
                    logger.log(f'Portainer instance [{name}]({host}) updated successfully.')
                else:
                    logger.log(f'An error occurred while updating Portainer instance [{name}]({host}).', level='ERROR')

                # Delay to make sure the update is applied
                time.sleep(10)

            # Get portainer environments
            environments = portainer.get_environments()
            logger.log(f'Retrieved {len(environments)} environments for Portainer instance [{name}]({host}).')

            # Process each environment
            for env in environments:
                env_name = env.get('Name')
                env_id = env.get('Id')

                try:
                    # Clear images status
                    portainer.clear_images_status(env_id)
                    logger.log(f'Cleared images status for environment [{env_name}] in Portainer instance [{name}]({host}).')

                    # Get environment stacks
                    stacks = portainer.get_environment_stacks(env_id)
                    logger.log(f'Retrieved {len(stacks)} stacks for environment [{env_name}] in Portainer instance [{name}]({host}).')

                    # Process each stack
                    for stack in stacks:
                        try:
                            stack_name = stack.get('Name')

                            # Check if the stack is ignored
                            if stack_name in ignore_stack:
                                logger.log(f'Ignoring stack [{stack_name}] in environment [{env_name}] of Portainer instance [{name}]({host}).')
                                continue
                            
                            stack_id = stack.get('Id')

                            # Check if the stack is from git integration and if it needs to be updated
                            if stack.get('GitConfig') and not update_stacks_with_git:
                                logger.log(f'Skipping stack [{stack_name}] in environment [{env_name}] of Portainer instance [{name}]({host}) due to Git integration.')
                                continue

                            # Refresh the stack
                            needs_update = portainer.refresh_stack_images(stack_id).lower()
                            if needs_update in ('updated', 'skipped'):
                                logger.log(f'Stack [{stack_name}] in environment [{env_name}] of Portainer instance [{name}]({host}) is {needs_update}.')
                                continue

                            if stack.get('GitConfig'):
                                logger.log(f'Updating stack [{stack_name}] in environment [{env_name}] of Portainer instance [{name}]({host}) with Git integration.')
                                git_authentication = stack.get('GitConfig', {}).get('Authentication', {})
                                repository_git_credential_id = git_authentication.get('GitCredentialID')
                                repository_password = git_authentication.get('Password')
                                repository_username = git_authentication.get('Username')

                                repository_authentication = bool((repository_username and repository_password) or repository_git_credential_id)
                                repository_reference_name = stack.get('GitConfig', {}).get('ReferenceName')
                                env_vars = stack.get('Env', [])

                                portainer.update_stack_with_git(
                                    stack_id=stack_id,
                                    environment_id=env_id,
                                    repository_authentication=repository_authentication,
                                    repository_git_credential_id=repository_git_credential_id,
                                    repository_password=repository_password,
                                    repository_reference_name=repository_reference_name,
                                    repository_username=repository_username,
                                    env=env_vars,
                                    prune=purne_services )
                                logger.log(f'Stack [{stack_name}] updated successfully in environment [{env_name}] of Portainer instance [{name}]({host}).')
                                any_stack_updated = True
                            else:
                                logger.log(f'Updating stack [{stack_name}] in environment [{env_name}] of Portainer instance [{name}]({host}).')
                                webhook = stack.get('Webhook', '')
                                stack_file_content = portainer.get_stack_file_content(stack_id)
                                if not stack_file_content:
                                    logger.log(f'Stack file content for stack [{stack_name}] in environment [{env_name}] of Portainer instance [{name}]({host})is empty.', level='ERROR')
                                    continue
                                env_vars = stack.get('Env', [])

                                portainer.update_stack(
                                    stack_id=stack_id,
                                    environment_id=env_id,
                                    env=env_vars,
                                    stack_file_content=stack_file_content,
                                    prune=purne_services,
                                    webhook=webhook )
                                logger.log(f'Stack [{stack_name}] updated successfully in environment [{env_name}] of Portainer instance [{name}]({host}).')
                                any_stack_updated = True
                        except PortainerError as e:
                            logger.log(e, level='ERROR')
                            continue    

                    # Check if unused images should be deleted
                    if delete_unused_images_flag and any_stack_updated:
                        delete_unused_images(portainer=portainer, environment_id=env_id, environment_name=env_name, logger=logger, name=name, host=host)

                    any_stack_updated = False  # Reset for the next environment
                    logger.log(f'Finished processing environment [{env_name}] in Portainer instance [{name}]({host}).')

                except PortainerError as e:
                    logger.log(e, level='ERROR')
                    continue    

                logger.log(f'Finished processing Portainer instance [{name}]({host}).')

        except PortainerError as e:
            logger.log(e, level='ERROR')
            continue

    logger.log('Processing completed for all Portainer instances.')

if __name__ == '__main__':
    main()
