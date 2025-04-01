from azure.identity.aio import DefaultAzureCredential, ClientSecretCredential
from azure.monitor.query.aio import LogsQueryClient, TokenCredential
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def query_azure_monitor(resource_id: str, query: str, time_span: timedelta):
    """
    Executa uma query em um recurso no Azure Monitor workspace em busca de logs.

    Parâmetros:
    - resource_id (str): ID do recurso a ser consultado.
    - query (str): Query Kusto a ser executada.
    - time_span (timedelta): Intervalo de tempo para a consulta.
    Retorno:
    - json: Saída do comando ou erro.
    """
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)
    #workspace_id = "/subscriptions/00ec1d2c-df0a-49cb-bb6c-848f54417bf5/resourceGroups/MAS-AKS-MVP/providers/microsoft.monitor/accounts/AMW-AKSMonitoring-001"
    results = []

    try:
        response = await client.query_resource(
            resource_id=resource_id,
            query=query,
            timespan=time_span,
        )

        if response.tables:
            for table in response.tables:
                for row in table.rows:
                    row_dict = dict(zip(table.columns_names, row))
                    results.append(row_dict)

        return json.dumps({"status": "success", "logs": results})

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
    
async def get_token(UseDefaultCredential: bool = True):
    """
    Obtém um token de acesso para autenticação no Azure.

    Parâmetros:
    - UseDefaultCredential (bool): Se True, utiliza as credenciais padrão do Azure.

    Retorno:
    - str: Token de acesso.
    """
    if UseDefaultCredential:
        credential = DefaultAzureCredential()
        token = await credential.get_token("https://management.azure.com/.default")
        return token.token
    else:
        credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
        scope = "https://management.azure.com/.default"
        token = await credential.get_token(scope)
        return token.access_token