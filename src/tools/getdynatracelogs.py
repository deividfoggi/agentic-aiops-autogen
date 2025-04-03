import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
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

def get_dynatrace_token():
    """Get Dynatrace authentication token"""
    auth_url = "https://sso.dynatrace.com/sso/oauth2/token"
    
    # Credentials should be moved to environment variables or secure configuration
    client_id = "dt0s02.66HVPTDH"
    client_secret = "dt0s02.66HVPTDH.C254KTHJ3KSX55HXRYMSKUWID55GOLMOMZJNGT6YL5YXRITKN3PLAPKEHFAIE2GN"
    account_urn = "urn:dtaccount:97ef9243-9098-48e0-a43a-c74900a84e02"
    
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": account_urn,
        "scope": "storage:metrics:read"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    response = requests.post(auth_url, data=data, headers=headers)
    response.raise_for_status()
    
    return response.json()["access_token"]

def build_query_from_problem(problem_json: Dict[Any, Any]) -> str:
    """
    Build a Dynatrace logs query based on the problem details
    """
    query_parts = []
    
    # Add entity information
    if problem_json.get("ImpactedEntities"):
        entity = problem_json["ImpactedEntities"][0]
        query_parts.append(f'entityName="{entity["name"]}"')
    
    # Add kubernetes information if available
    if "ProblemDetailsJSON" in problem_json and "rankedEvents" in problem_json["ProblemDetailsJSON"]:
        event = problem_json["ProblemDetailsJSON"]["rankedEvents"][0]
        if "customProperties" in event:
            props = event["customProperties"]
            if "k8s.namespace.name" in props:
                query_parts.append(f'k8s.namespace.name="{props["k8s.namespace.name"]}"')
            if "k8s.cluster.name" in props:
                query_parts.append(f'k8s.cluster.name="{props["k8s.cluster.name"]}"')
            if "k8s.workload.name" in props:
                query_parts.append(f'k8s.workload.name="{props["k8s.workload.name"]}"')
    
    # Add severity and problem type information
    if problem_json.get("ProblemSeverity"):
        query_parts.append(f'severity="{problem_json["ProblemSeverity"]}"')
    
    # Combine all parts with AND
    return " AND ".join(query_parts)

def get_dynatrace_logs(problem_json: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Get relevant logs from Dynatrace based on a problem JSON
    
    Args:
        problem_json (dict): Problem details from Dynatrace in JSON format
        
    Returns:
        dict: JSON response from Dynatrace API containing relevant logs
    """
    try:
        token = get_dynatrace_token()
        
        # Extract time window from problem
        problem_details = problem_json.get("ProblemDetailsJSON", {})
        start_time = problem_details.get("startTime", None)
        end_time = problem_details.get("endTime", None)
        
        # Convert milliseconds to proper format or use default time window
        if start_time and end_time:
            start_time = datetime.fromtimestamp(start_time/1000).isoformat() + "Z"
            end_time = datetime.fromtimestamp(end_time/1000).isoformat() + "Z"
        else:
            # Default to last hour if no time window provided
            end_time = "now"
            start_time = "now-1h"
        
        # Build query based on problem details
        query = build_query_from_problem(problem_json)
        
        url = "https://tts08128.live.dynatrace.com/api/v2/logs/search"
        
        params = {
            "query": query,
            "from": start_time,
            "to": end_time,
            "limit": 100  # Adjust limit as needed
        }
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return {
            "query_used": query,
            "time_window": {
                "from": start_time,
                "to": end_time
            },
            "results": response.json()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query_attempted": query if 'query' in locals() else None,
            "time_window_attempted": {
                "from": start_time if 'start_time' in locals() else None,
                "to": end_time if 'end_time' in locals() else None
            }
        }
