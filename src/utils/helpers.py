import sys
import os
import shutil

def resource_path(relative_path):
    """Get absolute path to resource, works in dev and compiled versions."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def init_config(target_path):
    """Initialize the configuration file by copying the example configuration."""
    example_path = resource_path(os.path.join('..', 'resources', 'example-config.yml'))

    if os.path.exists(target_path):
        print(f"The file '{target_path}' already exists. Please remove it before generating a new configuration.")
        return
    
    if not os.path.exists(example_path):
        print(f"Example file '{example_path}' not found.")
        return
    
    # Ensure the target directory exists
    target_dir = os.path.dirname(target_path)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Copy the example configuration file to the target path    
    shutil.copyfile(example_path, target_path)
    print(f"Configuration file created at: {target_path}")