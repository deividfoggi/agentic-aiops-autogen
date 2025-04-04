from fastapi import FastAPI, HTTPException, Request
import asyncio
from pydantic import BaseModel
from typing import Any
from utils.agents import Agents
from tools.queryazmonitor import query_azure_monitor
from datetime import timedelta
import json
from utils.logger import logger

# Set up logging
logger = logger.setup_logger(__name__)

class APIEndpoint:
    """
    A class to define and manage a FastAPI application with specific routes and background task handling.
    Methods:
        __init__():
            Initializes the FastAPI application, sets up routes, and initializes a set for background tasks.
        setup_routes():
            Defines the routes for the FastAPI application. Currently includes:
                - POST /alert: Processes incoming JSON payloads, triggers background tasks, and handles errors.
        get_app():
            Returns the FastAPI application instance.
    Routes:
        POST /alert:
            Processes a JSON payload from the request body, converts it to a string, and triggers a background task
            using the `Agents.run_task` method. Handles any exceptions that occur during processing.
            Returns:
                - A JSON response with a success status and HTTP 200 on successful processing.
                - Raises an HTTPException with status code 500 and error details on failure.
    """
    def __init__(self):
        self.app = FastAPI()
        self.background_tasks = set()
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/alert")
        async def process_payload(request: Request):
            try:
                # Log the incoming request
                logger.info(f"Received request from {request.client.host} with headers: {request.headers}")
                
                # Read the request body
                payload = await request.json()

                # Convert the JSON payload to a string
                event_str = json.dumps(payload)
                
                # Initialize the Agents class instance
                agents = Agents()
                
                # Create an asynchronous task to run the agent's task with the event string
                task = asyncio.create_task(agents.run_task(event_str))
                
                # Add the created task to the set of background tasks
                self.background_tasks.add(task)
                
                # Ensure the task is removed from the set once it is completed
                task.add_done_callback(self.background_tasks.discard)
                
                # Return a success response with HTTP status 200
                return {"status": "success"}, 200

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing payload: {str(e)}"
                )
    
    # Method to return the FastAPI application instance
    def get_app(self):
        return self.app
    
# Create an instance of the APIEndpoint class
api = APIEndpoint()

# Retrieve the FastAPI application instance from the APIEndpoint instance
app = api.get_app()

# Define an event handler for the "startup" event
@app.on_event("startup")
async def startup_event():
    # Placeholder for any startup logic (currently does nothing)
    pass

# Define an event handler for the "shutdown" event
@app.on_event("shutdown")
async def shutdown_event():
    # Check if there are any background tasks still running
    if api.background_tasks:
        # Wait for all background tasks to complete before shutting down
        await asyncio.gather(*api.background_tasks)