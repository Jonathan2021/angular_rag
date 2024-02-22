from rag.blocks.pipelines import VectorPipelineFromConfig
from rag.utils import config_loader

def main():

    args, config=config_loader()

    pipeline = VectorPipelineFromConfig(config)
    if args.verbose:
        print("Created pipeline")
    
    result = pipeline.process()
    
    if args.verbose:
        print("Processing complete.")
        print("Result:", result)

if __name__ == "__main__":
    main()
