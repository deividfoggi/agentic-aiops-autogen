# help me to create a config.py file for a python project used to get all environment variables needed for the project
import os
from dotenv import load_dotenv
from pathlib import Path
# Load environment variables from .env file
load_dotenv()
# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Define the environment variables

class Config:
    port = os.getenv('PORT')
    aoai_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
    aoai_model = os.getenv('AZURE_OPENAI_MODEL')
    aoai_version = os.getenv('AZURE_OPENAI_API_VERSION')
    aoai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    aoai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
    dynatrace_api_key = os.getenv('DYNATRACE_API_KEY')
    dynatrace_api_endpoint = os.getenv('DYNATRACE_API_ENDPOINT', 'https://tts08128.live.dynatrace.com/api/v2/logs/search')
    az_resourcegroup = os.getenv('RESOURCE_GROUP')
    az_aks_name = os.getenv('AKS_CLUSTER_NAME')
    azm_workspace_id = os.getenv('AZURE_MONITOR_WORKSPACE_ID')
    dynatrace_client_id = os.getenv('DYNATRACE_CLIENT_ID')
    dynatrace_client_secret = os.getenv('DYNATRACE_CLIENT_SECRET')
    dynatrace_account_urn = os.getenv('DYNATRACE_ACCOUNT_URN')
    environment = os.getenv('ENVIRONMENT')