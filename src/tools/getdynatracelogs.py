import os
from dotenv import load_dotenv
from utils.httpclient import HttpClient
from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated
import asyncio

load_dotenv()

api_url = os.getenv("DYNA_TRACE_API_URL")
api_key = os.getenv("DYNA_TRACE_API_KEY")
http_client = HttpClient(api_url, api_key)

async def get_dynatrace_logs(path: str, query: str):
    # get logs using the HttpClient
    response = http_client.get(f"{path}{query}")
    return response

get_dynatracelogs_tool = FunctionTool(
    get_dynatrace_logs,
    description="Get logs from DynaTrace",
    name="get_dynatrace_logs",
    strict=True
)