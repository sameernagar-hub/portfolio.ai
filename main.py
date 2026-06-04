import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Sameer Nagar AI Portfolio Backend")

# Enable CORS for local development and frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.portfolio_db

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

PROFILE_CONTEXT = """
Sameer Nagar is a Software Development Engineer. 
MS in Computer Science from CSU Fullerton (Graduated May 2026, GPA 3.7).
Former Software Engineer at Unthinkable Solutions.
Expertise: Python, Java, AWS, Agentic AI, and Scalable Backend Systems.
"""

# Configure Gemini with System Instruction
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=f"You are Sameer's Portfolio Assistant. Context: {PROFILE_CONTEXT}"
)

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="Gemini API Key not configured on server.")

    try:
        # Initialize chat with history
        chat = model.start_chat(history=[
            {"role": "user" if m.role == "user" else "model", "parts": [m.content]}
            for m in request.history
        ])

        response = chat.send_message(request.message)
        
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def get_projects():
    """Fetch dynamic project data from MongoDB."""
    try:
        projects = await db.projects.find().to_list(100)
        for project in projects:
            project["_id"] = str(project["_id"])
        return projects
    except Exception as e:
        return {"error": "Could not fetch projects", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)