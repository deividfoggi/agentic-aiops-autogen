import os
from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from tools.getdynatracelogs import get_dynatracelogs_tool
from utils.config import Config

load_dotenv()

class Agents:
    def __init__(self):
        self.az_model_client = AzureOpenAIChatCompletionClient(
            azure_deployment=Config.aoai_deployment,
            model=Config.aoai_model,
            api_version=Config.aoai_version,
            azure_endpoint=Config.aoai_endpoint,
            api_key=Config.aoai_api_key
        )

        self.assistant = AssistantAgent(
            name="Assistant",
            model_client=self.az_model_client,
            tools=[get_dynatracelogs_tool],
        )

        self.team = MagenticOneGroupChat([self.assistant], model_client=self.az_model_client)
    
    async def run_task(self, task:str):
        """
            Runs a specific task with the configured agents
        
            Args:
                task (str): The task to be performed by the agents
        """
    
        await Console(self.team.run_stream(task=task))
        