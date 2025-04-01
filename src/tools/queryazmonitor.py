from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import LogsQueryClient
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
import aiohttp
from autogen_agentchat.ui import Console
from utils.config import Config

load_dotenv()

class DateTimeEncoder(json.JSONEncoder):
    """
    Classe para serializar objetos datetime em JSON.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

#No momento, o workspace_id esta sendo passado via environment variable, mas precisa ser passado via parametro, quando a funcion calling ocorrer
async def query_azure_monitor(query: str, time_span: timedelta):
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
    workspace_id = Config.get("AZURE_MONITOR_WORKSPACE_ID")
    results = []

    try:
        response = await client.query_workspace(
            workspace_id=workspace_id,
            query=query,
            timespan=time_span
        )

        if response.tables:
            for table in response.tables:
                for row in table.rows:
                    row_dict = dict(zip(table.columns, row))
                    results.append(row_dict)

        query_result = json.dumps({"status": "success", "logs": results}, cls=DateTimeEncoder)
        return query_result

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
    finally:
        await credential.close()
        await client.close()