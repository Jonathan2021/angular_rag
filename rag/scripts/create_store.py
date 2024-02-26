import argparse
from dotenv import load_dotenv
import os
from rag.blocks.pipelines import VectorPipelineFromConfig
from rag.utils import load_configuration

def main():
    parser = argparse.ArgumentParser(description="Process a configuration for the pipeline.")
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

    pipeline = VectorPipelineFromConfig(config)
    if args.verbose:
        print("Created pipeline")
    
    result = pipeline.process()
    
    if args.verbose:
        print("Processing complete.")
        print("Result:", result)

if __name__ == "__main__":
    main()
