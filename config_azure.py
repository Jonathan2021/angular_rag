# AZURE AI SEARCH CONFIGURATION
from dotenv import load_dotenv
from dotenv import dotenv_values
import os

load_dotenv()
root_dir=os.path.dirname(__file__)
values_env = dotenv_values(os.path.join(root_dir,".env"))

# AZURE AI SEARCH CONFIGURATION
searchservice = values_env['searchservice']
service_name = values_env['service_name']
searchkey = values_env['searchkey']
category=values_env['category']

#AZURE STORAGE CONFIGURATION
storageaccount  = values_env['storageaccount']
container=values_env['container']
storagekey=values_env['storagekey']


##AZURE FORM RECOGNIZER CONFIGURATION
formrecognizerservice=values_env['formrecognizerservice']
formrecognizerkey=values_env['formrecognizerkey']


#OPEN AI API CONFIGURATION
openai_api_key = values_env['openai_api_key']
openai_api_location = values_env['openai_api_location']
openai_api_endpoint = values_env['openai_api_endpoint']
deployment_id_gpt=values_env['deployment_id_gpt']
deployment_id_gpt_embedding=values_env['deployment_id_gpt_embedding'] 
openai_api_version=values_env['openai_api_version'] 
