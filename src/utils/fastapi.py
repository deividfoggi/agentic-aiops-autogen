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
    # essa rota é somente para teste da tool queryazmonitor
        @self.app.post("/test-azmonitor")
        async def testazmonitor(event: TaskPayload):
            result = await query_azure_monitor(
                resource_id="/subscriptions/00ec1d2c-df0a-49cb-bb6c-848f54417bf5/resourceGroups/mas-aks-mvp/providers/Microsoft.ContainerService/managedClusters/MVP-AKS",
                query="""KubePodInventory | take 10""",
                time_span=timedelta(minutes=5)
            )
            return {f"status": "success", "message": "{result}"}, 200
    
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