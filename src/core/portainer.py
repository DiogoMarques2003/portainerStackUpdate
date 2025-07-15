import requests
from errors.portainer_error import PortainerError

class Portainer:
    def __init__(self, url: str, access_token: str, verify_ssl: bool = False):
        self.url = url

        # Initialize the session
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": access_token})

        # Disable SSL verification
        self.session.verify = verify_ssl

    def ping(self):
        """Ping the Portainer instance to check if it's reachable."""
        try:
            response = self.session.get(self.url)

            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to reach Portainer: {e}")
        
    def get_docker_api_version(self, environment_id: int):
        """Get the Docker API version for a specific environment."""
        try:
            response = self.session.get(f"{self.url}/api/endpoints/{environment_id}/docker/version")

            response.raise_for_status()

            return response.json().get('ApiVersion', '1.41')  # Default to 1.41 if not found
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to get Docker API version for environment {environment_id}: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
    
    def check_if_portainer_needs_update(self):
        """Check if the Portainer instance needs an update."""
        try:
            response = self.session.get(f"{self.url}/api/system/version")
        
            response.raise_for_status()
            
            return response.json().get('UpdateAvailable', False)
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to get Portainer version: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")

    def update_portainer_version(self):
        """Update the Portainer instance to the last version."""
        try:
            response = self.session.post(f"{self.url}/api/system/update")

            response.raise_for_status()

            return not response.json().get('UpdateAvailable', False)
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to update Portainer: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
        
    def get_environments(self):
        """Get the list of environments from Portainer."""
        try:
            response = self.session.get(f"{self.url}/api/endpoints")

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to get environments: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
        
    def get_environment_stacks(self, environment_id: int):
        """Get the stacks for a specific environment."""
        try:
            response = self.session.get(f"{self.url}/api/stacks?filters={{\"EndpointID\": {environment_id},\"IncludeOrphanedStacks\": {False}}}")

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to get stacks for environment {environment_id}: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
        
    def clear_images_status(self, environment_id: int):
        """Clear the status of images in a specific environment."""
        try:
            response = self.session.post(f"{self.url}/api/stacks/image_status/clear?environmentId={environment_id}")

            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to clear images status for environment {environment_id}: {e}")
        
    def refresh_stack_images(self, stack_id: int):
        """Refresh the images for a specific stack."""
        try:
            response = self.session.post(f"{self.url}/api/stacks/{stack_id}/images_status?refresh=true")

            response.raise_for_status()

            # Return the status of the images
            return response.json().get('Status', 'updated')
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to refresh images for stack {stack_id}: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
        
    def update_stack(self, stack_id: int, environment_id: int, env: list[str], stack_file_content: str, prune: bool, webhook: str):
        """Update a stack in a specific environment."""
        try:
            data = {
                "StackFileContent": stack_file_content,
                "Env": env,
                "id": environment_id,
                "PullImage": True,
                "Prune": prune,
                "Webhook": webhook
            }
            response = self.session.put(f"{self.url}/api/stacks/{stack_id}?endpointId={environment_id}", json=data)

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to update stack {stack_id} in environment {environment_id}: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
        
    def update_stack_with_git(self, stack_id: int, environment_id: int, repository_authentication: bool, repository_git_credential_id: int, repository_password: str,
                            repository_reference_name: str, repository_username: str, env: list[str], prune: bool):
        """Update a stack in a specific environment using Git."""
        try:
            data = {
                "PullImage": True,
                "RepositoryAuthentication": repository_authentication,
                "RepositoryGitCredentialID": repository_git_credential_id,
                "RepositoryPassword": repository_password,
                "RepositoryReferenceName": repository_reference_name,
                "RepositoryUsername": repository_username,
                "Env": env,
                "Prune": prune
            }
            response = self.session.put(f"{self.url}/api/stacks/{stack_id}/git/redeploy?endpointId={environment_id}", json=data)

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to update stack {stack_id} in environment {environment_id} using Git: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
        
    def get_images_with_usage(self, environment_id: int):
        """Get images with usage in a specific environment."""
        try:
            response = self.session.get(f"{self.url}/api/docker/{environment_id}/images?withUsage=true")

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to get images with usage for environment {environment_id}: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
        
    def delete_image(self, environment_id: int, docker_api_version: str, image_id: str):
        """Delete an image from a specific environment."""
        try:
            response = self.session.delete(f"{self.url}/api/endpoints/{environment_id}/docker/v{docker_api_version}/images/{image_id}?force=false")

            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise PortainerError(f"Failed to delete image {image_id} from environment {environment_id}: {e}")
        except ValueError:
            raise PortainerError("Invalid response from Portainer API. Could not parse JSON.")
