import os
import requests
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from utils.httpclient import HttpClient
from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated
from utils.config import Config
import urllib.parse

load_dotenv()

api_endpoint = Config.dynatrace_api_endpoint
api_key = Config.dynatrace_api_key

http_client = HttpClient(api_endpoint, headers={"api-key": f"{api_key}"})

class DynatraceAuthError(Exception):
    """Exception raised for Dynatrace authentication errors"""
    pass

class DynatraceQueryError(Exception):
    """Exception raised for Dynatrace query errors"""
    pass

def get_dynatrace_token() -> str:
    """Get Dynatrace authentication token using the exact same logic as get_token_alt.sh"""
    try:
        # Credenciais exatamente como no script
        client_id = "dt0s02.66HVPTDH"
        client_secret = "dt0s02.66HVPTDH.C254KTHJ3KSX55HXRYMSKUWID55GOLMOMZJNGT6YL5YXRITKN3PLAPKEHFAIE2GN"
        account_urn = "urn:dtaccount:97ef9243-9098-48e0-a43a-c74900a84e02"
        environment_url = "tts08128.live.dynatrace.com"
        
        # Endpoint de autenticação
        auth_url = "https://sso.dynatrace.com/sso/oauth2/token"
        
        # Debug logs como no script
        print(f"Debug - Fazendo requisição para obter token (método alternativo)...")
        print(f"Debug - Client ID: {client_id}")
        print(f"Debug - Account URN: {account_urn}")
        print(f"Debug - Environment URL: {environment_url}")
        
        # Preparar os dados exatamente como no script (usando --data-urlencode)
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "resource": account_urn,
            "scope": "storage:logs:read storage:buckets:read"  # Note o scope diferente aqui!
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Fazer a requisição
        response = requests.post(auth_url, data=data, headers=headers)
        
        print(f"Debug - Resposta da API:")
        print(f"Debug - {response.text}")
        
        if response.status_code != 200:
            raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
        
        response_json = response.json()
        if "access_token" not in response_json:
            raise Exception("No access token in response")
            
        token = response_json["access_token"]
        print(f"Debug - Token extraído com sucesso")
        
        return token
        
    except Exception as e:
        raise Exception(f"Error getting token: {str(e)}")

# def build_query_from_problem(problem_json: Dict[Any, Any]) -> str:
#     """Build a Dynatrace logs query based on the problem details"""
#     if not isinstance(problem_json, dict):
#         raise DynatraceQueryError("Problem JSON must be a dictionary")
    
#     query_parts = []
    
#     try:
#         # Add entity information
#         if "entityName" in problem_json.get("rankedEvents", [{}])[0]:
#             entity_name = problem_json["rankedEvents"][0]["entityName"]
#             query_parts.append(f'entityName="{entity_name}"')
        
#         # Add kubernetes information
#         if "customProperties" in problem_json.get("rankedEvents", [{}])[0]:
#             props = problem_json["rankedEvents"][0]["customProperties"]
#             for k8s_prop in ["k8s.namespace.name", "k8s.cluster.name", "k8s.workload.name"]:
#                 if k8s_prop in props:
#                     query_parts.append(f'{k8s_prop}="{props[k8s_prop]}"')
        
#         # Add severity information
#         if "severityLevel" in problem_json:
#             query_parts.append(f'severity="{problem_json["severityLevel"]}"')
        
#         if not query_parts:
#             raise DynatraceQueryError("Could not extract any valid query parameters from problem JSON")
        
#         return " AND ".join(query_parts)
        
#     except Exception as e:
#         raise DynatraceQueryError(f"Error building query from problem JSON: {str(e)}")

def get_dynatrace_logs(
    problem_json: Optional[Dict[Any, Any]] = None,
    query: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100
) -> Dict[Any, Any]:
    """
    Get logs from Dynatrace using DQL sintax.
    Args:
        problem_json (dict): JSON object containing problem details in the Dyna Trace problem schema.
        query (str): Custom query string using DQL syntax.
        start_time (str): Start time for the logs in iso8601 format.
        end_time (str): End time for the logs in iso8601 format.
        limit (int): Number of logs to retrieve.
    """
    try:
        # Obter o token
        try:
            token = get_dynatrace_token()
            print(f"Debug - Token obtained successfully")  # Debug log
        except Exception as e:
            print(f"Debug - Token error: {str(e)}")  # Debug log
            return {"error": str(e), "status": "auth_error"}
        
        # # Construir a query
        # if problem_json:
        #     query_parts = []
            
        #     if "rankedEvents" in problem_json and problem_json["rankedEvents"]:
        #         event = problem_json["rankedEvents"][0]
        #         if "customProperties" in event:
        #             props = event["customProperties"]
        #             if "k8s.namespace.name" in props:
        #                 query_parts.append(f'k8s.namespace.name="{props["k8s.namespace.name"]}"')
        #             if "k8s.cluster.name" in props:
        #                 query_parts.append(f'k8s.cluster.name="{props["k8s.cluster.name"]}"')
        #             if "k8s.workload.name" in props:
        #                 query_parts.append(f'k8s.workload.name="{props["k8s.workload.name"]}"')
                
        #         # Adicionar informações do evento
        #         if "severityLevel" in event:
        #             query_parts.append(f'severity="{event["severityLevel"]}"')
        #         if "eventType" in event:
        #             query_parts.append(f'eventType="{event["eventType"]}"')
            
        #     final_query = " AND ".join(query_parts) if query_parts else "Severity:info"
            
        #     # Usar os timestamps do problema
        #     if "startTime" in problem_json:
        #         start_time = datetime.fromtimestamp(problem_json["startTime"]/1000).strftime("%Y-%m-%dT%H:%M:%SZ")
        #     if "endTime" in problem_json:
        #         end_time = datetime.fromtimestamp(problem_json["endTime"]/1000).strftime("%Y-%m-%dT%H:%M:%SZ")
        # else:
        #     final_query = query if query else "Severity:info"
        
        # # Garantir valores default para tempos
        # if not start_time:
        #     start_time = "now-1h"
        # if not end_time:
        #     end_time = "now"
        
        # # Codificar a query
        # encoded_query = urllib.parse.quote(final_query)
        
        # Fazer a requisição exatamente como no script testeapixp
        url = "https://tts08128.live.dynatrace.com/api/v2/logs/search"
        params = {
            "query": query,
            "from": start_time,
            "to": end_time,
            "limit": limit
        }
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print(f"Debug - Making request with params: {params}")  # Debug log
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Debug - Log search failed: {response.status_code} - {response.text}")  # Debug log
            return {
                "error": f"Log search failed: {response.status_code} - {response.text}",
                "status": "error",
                "query_used": query
            }
        
        return {
            "status": "success",
            "query_used": query,
            "time_window": {"from": start_time, "to": end_time},
            "results": response.json()
        }
        
    except Exception as e:
        print(f"Debug - Unexpected error: {str(e)}")  # Debug log
        return {
            "error": f"Unexpected error: {str(e)}", 
            "status": "error",
            "query_attempted": final_query if 'final_query' in locals() else None,
            "parameters": {
                "start_time": start_time if 'start_time' in locals() else None,
                "end_time": end_time if 'end_time' in locals() else None,
                "limit": limit
            }
        }