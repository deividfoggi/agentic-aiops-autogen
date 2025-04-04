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

# Set up logging
logger = logger.setup_logger(__name__)

class DynatraceAuthError(Exception):
    """Exception raised for Dynatrace authentication errors"""
    pass

class DynatraceQueryError(Exception):
    """Exception raised for Dynatrace query errors"""
    pass

def get_dynatrace_token() -> str:
    """
    Get a token from Dynatrace using client credentials.
    Returns:
        str: The access token for authentication.
    """
    try:
        # Define the authentication URL for Dynatrace
        auth_url = "https://sso.dynatrace.com/sso/oauth2/token"
        
        # Prepare the data payload for the authentication request
        data = {
            "grant_type": "client_credentials",  # Specify the grant type for client credentials
            "client_id": Config.dynatrace_client_id,  # Client ID from the configuration
            "client_secret": Config.dynatrace_client_secret,  # Client secret from the configuration
            "resource": Config.dynatrace_account_urn,  # Dynatrace account URN
            "scope": "storage:logs:read storage:buckets:read"  # Scopes for the requested permissions
        }
        
        # Set the headers for the authentication request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"  # Specify the content type for form data
        }
        
        # Make a POST request to the authentication URL with the data and headers
        response = requests.post(auth_url, data=data, headers=headers)
        
        # Check if the response status code indicates an error
        if response.status_code != 200:
            # Log the error details
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            # Raise an exception with the error details
            raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
        
        # Parse the JSON response from the authentication request
        response_json = response.json()
        
        # Check if the access token is present in the response
        if "access_token" not in response_json:
            # Log an error if the access token is missing
            logger.error("No access token in response")
            # Raise an exception indicating the missing token
            raise Exception("No access token in response")
        
        # Extract the access token from the response
        token = response_json["access_token"]
        # Print a debug message indicating successful token extraction
        print(f"Debug - Token extraído com sucesso")
        
        # Return the extracted access token
        return token
        
    except Exception as e:
        # Raise an exception with the error details if any error occurs
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
        # Attempt to retrieve the Dynatrace token
        try:
            logger.info("Attempting to get Dynatrace token")  # Log the start of the token retrieval process
            token = get_dynatrace_token()  # Call the function to get the Dynatrace token
            logger.info("Token obtained successfully")  # Log success after obtaining the token
        except Exception as e:
            # Handle any exceptions that occur during token retrieval
            logger.error(f"Failed to get Dynatrace token: {str(e)}")  # Log the error details
            return {"error": str(e), "status": "auth_error"}  # Return an error response with details
        
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
        
        # Construct the URL for the Dynatrace logs query endpoint
        url = Config.dynatrace_api_endpoint + "/api/v2/logs/query"
        
        # Define the query parameters for the API request
        params = {
            "query": query,  # The DQL query string
            "from": start_time,  # Start time for the logs
            "to": end_time,  # End time for the logs
            "limit": limit  # Maximum number of logs to retrieve
        }
        
        # Set up the headers for the API request, including the authorization token
        headers = {
            "Authorization": f"Bearer {token}"  # Bearer token for authentication
        }
        
        # Log the request details for debugging purposes
        logger.info(f"Debug - Making request to {url} with params: {params}")
        
        # Make the GET request to the Dynatrace API
        response = requests.get(url, params=params, headers=headers)
        
        # Check if the response status code indicates an error
        if response.status_code != 200:
            # Log the error details
            logger.error(f"Log search failed: {response.status_code} - {response.text}")
            # Return an error response with details
            return {
            "error": f"Log search failed: {response.status_code} - {response.text}",
            "status": "error",
            "query_used": query  # Include the query used in the response
            }
        
        # Log a success message if the request was successful
        logger.info("Log search completed successfully")
        
        # Return the successful response with the query results
        return {
            "status": "success",  # Indicate success
            "query_used": query,  # Include the query used
            "time_window": {"from": start_time, "to": end_time},  # Include the time window
            "results": response.json()  # Include the JSON response from the API
        }
        
        except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        # Return an error response with details about the exception
        return {
            "error": f"Unexpected error: {str(e)}",  # Include the error message
            "status": "error",  # Indicate an error occurred
            "query_attempted": final_query if 'final_query' in locals() else None,  # Include the attempted query if available
            "parameters": {  # Include the parameters used in the request
            "start_time": start_time if 'start_time' in locals() else None,
            "end_time": end_time if 'end_time' in locals() else None,
            "limit": limit
            }
        }