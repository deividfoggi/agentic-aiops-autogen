from dotenv import load_dotenv
from utils.httpclient import HttpClient
from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated
from utils.config import Config

load_dotenv()

api_endpoint = Config.dynatrace_api_endpoint
api_key = Config.dynatrace_api_key

http_client = HttpClient(api_endpoint, headers={"api-key": f"{api_key}"})

async def get_dynatrace_logs(path: str, query: str):
    # get logs using the HttpClient
    response = http_client.send_request(api_endpoint, "get", f"{path}?{query}")
    return response