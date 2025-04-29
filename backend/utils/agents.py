from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent #, MultimodalWebSurfer
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from tools.getdynatracelogs import get_dynatrace_logs
from tools.shell import shell
from tools.queryazmonitor import query_azure_monitor
from utils.config import Config
from utils.prompthandler import get_prompt
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from utils.logger import setup_logger

load_dotenv()

# Set up logging
logger = setup_logger(__name__)

class Agents:
    def __init__(self):
        """
        Initializes the Agents class, setting up the Azure OpenAI Chat Completion Client and creating specialized agents.
        The agents are designed to handle specific tasks related to Dynatrace logs, shell commands, and Azure Monitor queries.
        The class also creates a team of agents for collaborative tasks.
        The Azure OpenAI Chat Completion Client is initialized based on the environment configuration.
        """
        
        # Initialize the Azure OpenAI Chat Completion Client based on the environment
        if Config.environment == "dev":
            # Use API key authentication for development environment
            self.az_model_client = AzureOpenAIChatCompletionClient(
                azure_deployment=Config.aoai_deployment,
                model=Config.aoai_model,
                api_version=Config.aoai_version,
                azure_endpoint=Config.aoai_endpoint,
                api_key=Config.aoai_api_key
            )
        else:
            # Use Azure AD token provider for non-development environments
            token_provider = get_bearer_token_provider(DefaultAzureCredential(), Config.llm_model_scope)
            self.az_model_client = AzureOpenAIChatCompletionClient(
                azure_deployment=Config.aoai_deployment,
                model=Config.aoai_model,
                api_version=Config.aoai_version,
                azure_endpoint=Config.aoai_endpoint,
                azure_ad_token_provider=token_provider
            )

        # Create an agent specialized in handling Dynatrace logs
        self.dynatrace_specialist = AssistantAgent(
            name="dynatrace_specialist",
            model_client=self.az_model_client,
            system_message=get_prompt("dynatrace_specialist"),
            tools=[get_dynatrace_logs]
        )

        # Create an agent specialized in executing shell commands
        self.aks_specialist = AssistantAgent(
            name="aks_specialist",
            model_client=self.az_model_client,
            system_message=get_prompt("aks_specialist"),
            tools=[shell]
        )

        # Create an agent specialized in querying Azure Monitor using KQL
        self.azuremonitor_specialist = AssistantAgent(
            name="azuremonitor_specialist",
            model_client=self.az_model_client,
            system_message=get_prompt("azuremonitor_specialist"),
            tools=[query_azure_monitor]
        )

        # Create a team of agents for collaborative tasks
        self.team = MagenticOneGroupChat([self.aks_specialist, self.azuremonitor_specialist], model_client=self.az_model_client)
    
    async def run_task(self, event: str, stream_handler=None):
        """
        Runs a specific task with the configured agents and streams the output.

        Args:
            event (str): The task to be performed by the agents.
            stream_handler (callable, optional): A handler to process streamed messages.
        """
        # Stream the output using the provided handler or default to the console
        if stream_handler:
            async for message in self.team.run_stream(task=event):
                # Log the message to the console
                logger.info(f"Agent Message: {message}")

                # Send the message to the stream handler (e.g., WebSocket)
                await stream_handler(message)
        else:
            # Default to streaming to the console
            async for message in self.team.run_stream(task=event):
                # Convert TextMessage to a dictionary if necessary
                if hasattr(message, "to_dict"):
                    message = message.to_dict()
                elif isinstance(message, str):
                    message = {"content": message}

                # Log the message to the console
                logger.info(f"Agent Message: {message}")

                # Stream the message to the console
                print(message)