from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prompt import SYSTEM_PROMPT_TASK, SYSTEM_PROMPT_PLANNER, SYSTEM_PROMPT_COACH
from schema import TodoTask
import json
import re
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_TOKEN") # Changed to HF_TOKEN to match .env and test.py
# Using Llama-3.3-70B-Instruct for high intelligence and instruction following
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct:together"

app = FastAPI(
    title="Plex ToDo AI API",
    description="AI-powered backend for Plex ToDo app. Converts natural language to structured tasks.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputText(BaseModel):
    text: str

def detect_mode(text: str) -> str:
    """Classify user intent into TASK, PLANNER, COACH, or CHAT."""
    t = text.lower()

    # Task keywords (adding, scheduling)
    if any(k in t for k in ["add", "remind", "schedule", "buy", "submit", "finish", "call", "appointment"]):
        return "TASK"

    # Planner keywords (organizing, optimizing)
    if any(k in t for k in ["plan", "organize", "schedule my", "routine", "optimize", "structure"]):
        return "PLANNER"

    # Coach keywords (emotions, support)
    if any(k in t for k in ["stress", "tired", "sad", "overwhelmed", "anxious", "motivate", "stuck", "burnout"]):
        return "COACH"

    # Default to CHAT if ambiguous, but for this specific app, 
    # if it looks like a task but missed keywords, we might want to default to TASK.
    # But strictly following the plan:
    return "CHAT"

async def query_hf_api(payload):

    if not HF_API_KEY:
        # Fallback for demo/testing if no key provided, but warn user
        print("Warning: HF_API_KEY not set. API calls might fail or be rate limited.")
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(HF_API_URL, headers=headers, json=payload, timeout=30.0)
        return response.json()

from fastapi.responses import FileResponse, RedirectResponse

# ... (other imports)

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Plex ToDo AI"}

@app.post("/ai")
async def ai_router(data: InputText):
    mode = detect_mode(data.text)
    print(f"Detected Mode: {mode}") # Debug logging

    if mode == "TASK":
        return await handle_task_mode(data.text)
    
    if mode == "PLANNER":
        return await handle_planner_mode(data.text)
    
    if mode == "COACH":
        return await handle_coach_mode(data.text)
    
    # Fallback/Chat mode
    return await handle_chat_mode(data.text)

# --- Mode Handlers ---

async def handle_task_mode(text: str):
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_TASK},
            {"role": "user", "content": text}
        ],
        "max_tokens": 500,
        "temperature": 0.1 # Low temp for precision
    }
    
    api_response = await call_api_wrapper(payload)
    content = extract_content(api_response)
    
    # Extract JSON
    import re
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        # If strict parsing fails, return a basic task object constructed from text
        # or raise error. let's try to be resilient.
        raise HTTPException(status_code=500, detail="Failed to parse task JSON from AI response")
        
    try:
        task_json = json.loads(match.group())
        return task_json
    except json.JSONDecodeError:
         raise HTTPException(status_code=500, detail="Invalid JSON from AI")

async def handle_planner_mode(text: str):
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_PLANNER},
            {"role": "user", "content": text}
        ],
        "max_tokens": 1000,
        "temperature": 0.7 # Higher temp for creativity
    }
    
    api_response = await call_api_wrapper(payload)
    content = extract_content(api_response)
    
    # Expecting JSON
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
            
    # Fallback if no JSON found (shouldn't happen with good prompt)
    return {"summary": "Plan generated", "details": content}

async def handle_coach_mode(text: str):
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_COACH},
            {"role": "user", "content": text}
        ],
        "max_tokens": 300,
        "temperature": 0.8 # Warm and empathetic
    }
    
    api_response = await call_api_wrapper(payload)
    content = extract_content(api_response)
    return {"role": "coach", "message": content}

async def handle_chat_mode(text: str):
    # Basic chat fallback
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ],
        "max_tokens": 500
    }
    api_response = await call_api_wrapper(payload)
    return {"role": "chat", "message": extract_content(api_response)}

# --- Helpers ---

async def call_api_wrapper(payload):
    try:
        return await query_hf_api(payload)
    except Exception as e:
        print(f"API Exception: {e}")
        raise HTTPException(status_code=503, detail=f"API Connection Error: {str(e)}")

def extract_content(api_response):
    if isinstance(api_response, dict) and "error" in api_response:
        raise HTTPException(status_code=500, detail=f"AI Model Error: {api_response['error']}")
    
    try:
        if "choices" in api_response and len(api_response["choices"]) > 0:
            return api_response["choices"][0]["message"]["content"]
        else:
            return str(api_response)
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Invalid API response format: {str(e)}")

# Keep legacy endpoint for now, mapped to task mode
@app.post("/parse-task", response_model=TodoTask)
async def parse_task(data: InputText):
    # Force TASK mode for this endpoint
    return await handle_task_mode(data.text)

