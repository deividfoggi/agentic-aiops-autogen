# create a http client for sending requests to the server
import requests
from requests.exceptions import RequestException
from typing import Dict, Any, Optional
import logging
import json
import os

class HttpClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.headers = headers if headers else {}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        #logging.basicConfig(level=logging.INFO)

    def send_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = os.path.join(self.base_url, endpoint)
        try:
            response = self.session.request(method, url, json=data)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except RequestException as e:
            logging.error(f"Request failed: {e}")
            return None