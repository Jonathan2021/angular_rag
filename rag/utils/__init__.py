import yaml
import argparse
import os
from dotenv import load_dotenv

def load_configuration(path):
    # Load and return the configuration from the YAML file
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def config_loader():
    parser = argparse.ArgumentParser(description="Process configuration.")
    parser.add_argument("--config", required=True, help="Path to the configuration file.")
    parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose mode.")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        raise FileNotFoundError(f"The configuration file {args.config} does not exist.")

    config = load_configuration(args.config)

    if "env_path" in config:
        load_dotenv(dotenv_path=config["env_path"])

    if args.verbose:
        print("Loaded config")

    return args, config