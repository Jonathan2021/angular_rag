import yaml

def load_configuration(path):
    # Load and return the configuration from the YAML file
    with open(path, 'r') as file:
        return yaml.safe_load(file)