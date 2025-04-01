from fastapi import FastAPI, HTTPException
import asyncio
from pydantic import BaseModel
from typing import Any
from utils.agents import Agents
from tools.queryazmonitor import query_azure_monitor
from datetime import timedelta

class TaskPayload(BaseModel):
    class Config:
        extra = "allow"

class APIEndpoint:
    def __init__(self):
        self.app = FastAPI()
        self.background_tasks = set()
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/alert")
        async def process_payload(event: TaskPayload):
            try:
                # Simulate processing the payload
                print(f"Processing payload: {event}")
                event_str = str(event)
                agents = Agents()
                task = asyncio.create_task(agents.run_task(event_str))
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)
                
                return {"status": "success"}, 200
    
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing payload: {str(e)}"
                )
    
    def get_app(self):
        return self.app
    
api = APIEndpoint()
app = api.get_app()

@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    if api.background_tasks:
        await asyncio.gather(*api.background_tasks)