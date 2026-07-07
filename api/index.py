import os
import sys
import tempfile
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add agy-engine to python path so we can import from it
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agy-engine"))

# Setup GCP credentials if provided via env var (raw JSON string)
gcp_creds = os.getenv("GCP_CREDS_JSON")
if gcp_creds:
    try:
        temp_dir = tempfile.gettempdir()
        creds_path = os.path.join(temp_dir, "gcp-creds.json")
        with open(creds_path, "w") as f:
            f.write(gcp_creds)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        print(f"GCP Credentials written to {creds_path}")
    except Exception as e:
        print(f"Error writing GCP credentials: {e}")

# Import agents and db utilities from agy-engine
from google.antigravity import Agent
from agents.orchestrator import create_orchestrator_config

app = FastAPI(title="RoomGenius AI Backend", docs_url="/api/python/docs", openapi_url="/api/python/openapi.json")

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ModelRequest(BaseModel):
    provider: str
    modelName: str

@app.post("/api/python/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Create orchestrator config
        config = create_orchestrator_config(conversation_id=req.conversation_id)
        
        async with Agent(config) as agent:
            response = await agent.chat(req.message)
            response_text = await response.text()
            
            return {
                "status": "success",
                "response": response_text,
                "conversation_id": agent.conversation_id
            }
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/python/models")
async def switch_model_endpoint(req: ModelRequest):
    try:
        model_mapping = {
            "gemini-flash": "gemini-flash",
            "gemini-pro": "gemini-pro",
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini",
            "claude-sonnet": "claude-sonnet",
            "claude-haiku": "claude-haiku",
            "vertex-gemini-flash": "vertex-gemini-flash",
            "vertex-gemini-pro": "vertex-gemini-pro",
        }
        
        mapped_model = model_mapping.get(req.modelName, "gemini-flash")
        os.environ["AI_MODEL_NAME"] = mapped_model
        
        return {
            "status": "success",
            "provider": req.provider,
            "model_name": mapped_model,
            "message": f"สลับไปใช้โมเดล {mapped_model} เรียบร้อยแล้ว"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
