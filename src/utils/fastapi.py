from fastapi import FastAPI, HTTPException
import asyncio
from pydantic import BaseModel
from typing import Dict, Any
from utils.agents import Agents
from dotenv import load_dotenv
load_dotenv()

class TaskPayload(BaseModel):
    task: str

class APIEndpoint:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/wakeup")
        async def process_payload(payload: TaskPayload):
            try:
                # Simulate processing the payload
                print(f"Processing payload: {payload}")
                agents = Agents()
                await agents.run_task(payload.task)
                
                return {"status": "success", 
                        "message": "Payload processed successfully",
                        "data": payload
                }
    
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing payload: {str(e)}"
                )
            
    def get_app(self):
        return self.app
    
api = APIEndpoint()
app = api.get_app()