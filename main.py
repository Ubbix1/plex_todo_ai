from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prompt import SYSTEM_PROMPT
from schema import TodoTask
import json
import re
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
# Using Gemma-2B-IT for speed and efficiency (Google's lightweight model)
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"

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

@app.post("/parse-task", response_model=TodoTask)
async def parse_task(data: InputText):
    # Create Chat Completion Payload
    payload = {
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": data.text}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    # Call External API
    try:
        api_response = await query_hf_api(payload)
    except Exception as e:
        print(f"API Exception: {e}")
        raise HTTPException(status_code=503, detail=f"API Connection Error: {str(e)}")

    # Handle API errors
    if isinstance(api_response, dict) and "error" in api_response:
        raise HTTPException(status_code=500, detail=f"AI Model Error: {api_response['error']}")
        
    # Extract Content from Chat Completion Response
    try:
        if "choices" in api_response and len(api_response["choices"]) > 0:
            generated_text = api_response["choices"][0]["message"]["content"]
        else:
            # Fallback for debugging unknown format
            generated_text = str(api_response)
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Invalid API response format: {str(e)}")

    # Extract JSON safely
    match = re.search(r"\{.*\}", generated_text, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="Invalid AI output")

    try:
        task_json = json.loads(match.group())
        return task_json
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="JSON parse failed")
