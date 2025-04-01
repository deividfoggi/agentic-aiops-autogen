from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
#from tools.getdynatracelogs import get_dynatrace_logs
from tools.shell import shell
from tools.queryazmonitor import query_azure_monitor
from utils.config import Config
from utils.prompthandler import get_prompt

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
        #Comment out this agent to prevent it from being used during tests with Azure Monitor
        # self.dynatrace_specialist = AssistantAgent(
        #     name="Assistant",
        #     model_client=self.az_model_client,
        #     system_message=get_prompt("dynatrace_specialist"),
        #     tools=[get_dynatrace_logs]
        # )

        self.aks_specialist = AssistantAgent(
            name="aks_specialist",
            model_client=self.az_model_client,
            system_message=get_prompt("aks_specialist"),
            tools=[shell]
        )

        self.kql_specialist = AssistantAgent(
            name="kql_specialist",
            model_client=self.az_model_client,
            system_message=get_prompt("kql_specialist"),
            tools=[query_azure_monitor]
        )

        self.team = MagenticOneGroupChat([self.aks_specialist, self.kql_specialist], model_client=self.az_model_client)
    
    async def run_task(self, event:str):
        """
            Runs a specific task with the configured agents
        
            Args:
                task (str): The task to be performed by the agents
        """
    
        await Console(self.team.run_stream(task=event))