import yaml
from config_azure import *
import click
import glob

chosen_path=os.path.join(root_dir,"config-current.yml")

PREDEFINED_PATHS={path.split("\\")[-1]:path for path in glob.glob(os.path.join(root_dir,f"*.yml"))}

path=click.prompt('Choose a path or enter a custom one', type=click.Choice(list(PREDEFINED_PATHS.keys()) + ['custom']),default="config-default.yml")

if path == 'custom':
    chosen_path = click.prompt('Enter a custom path', type=click.Path(exists=False))
    print(f"Custom path provided: {chosen_path}")
    # You can use 'os.path' functions to work with the provided custom path
else:
    chosen_path = PREDEFINED_PATHS.get(path)
    if chosen_path:
        print(f"Predefined path selected: {chosen_path}")
        # You can use 'os.path' functions to work with the predefined path
    else:
        print("Invalid option, returning to default")

with open(chosen_path, 'r') as f:
    config = yaml.full_load(f)

config_load_and_split = config["config_load_and_split"]

config_index = config["config_index"]

config_chat = config["config_chat"]

config_azure_retriever = config["config_azure_retriever"]

config_QA_chain = config["config_QA_chain"]

config_conversation = config["config_conversation"]

if config_load_and_split["method_loading"] == "AzureAIDocumentIntelligenceLoader":
    config_load_and_split.update({"loader_kwargs": {"api_endpoint": formrecognizerservice,
                                                    "api_key": formrecognizerkey}})

if config_index["vector_store_map"] == "AzureSearch":
    config_index.update({"azure_search_endpoint": searchservice,
                         "azure_search_key": searchkey})

if config_index["embedding_map"] == "AzureOpenAIEmbeddings":
    config_index.update({"azure_endpoint": openai_api_endpoint,
                         "api_key": openai_api_key,
                         "api_version": openai_api_version,
                         "azure_deployment": deployment_id_gpt_embedding})

