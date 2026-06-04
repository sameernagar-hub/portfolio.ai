import os
import traceback
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
Sameer Nagar is a Software Development Engineer focused on backend systems, AI integration, cloud platforms, and full-stack delivery.

Contact:
- Email: nagarsam8989@gmail.com
- Phone: +1 (657) 751-9425
- Location: Fullerton, California
- LinkedIn: https://www.linkedin.com/in/aavonsameer/
- GitHub: https://github.com/sameernagar-hub

Education:
- Master of Science in Computer Science, California State University, Fullerton. Graduated May 2026, GPA 3.70/4.00.
- Bachelor of Technology in Computer Science, Rajiv Gandhi Proudyogiki Vishwavidyalaya, India, 2018 - 2022, GPA 3.66/4.00.

Experience:
- Jr. Associate Software Engineer, Unthinkable Solutions, Gurugram, India, 2021 - 2024. Built scalable backend services, full-stack applications, enterprise workflows, AI-powered solutions, LLM integrations, and automation.
- Teaching Associate, California State University, Fullerton, 2025 - 2026. Mentored students, supported computer science coursework, graded assignments, and collaborated with faculty.
- Service Associate, California State University, Fullerton, 2025 - 2026. Delivered customer service, transactions, inventory support, and team operations.

Skills:
- Python, Java, C++, JavaScript, React, Node.js, Flask, MySQL, MongoDB, AWS, Azure, Docker, CI/CD, LLMs, Prompt Engineering, Agentic AI, Salesforce Development.

Project themes:
- Scalable API services, LLM portfolio assistant, task manager application, ML pipeline automation, data pipeline services, cloud operations dashboard.
"""

# Configure Gemini with System Instruction
api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
if not api_key:
    print("ERROR: GEMINI_API_KEY is empty or missing in .env")
else:
    print(f"API Key loaded successfully (Length: {len(api_key)})")

# Using transport='rest' fixes 404/NotFound errors on many Windows/Python 3.14 setups
genai.configure(api_key=api_key, transport='rest')

model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
model = genai.GenerativeModel(
    model_name=model_name,
    system_instruction=f"You are Sameer Nagar's Professional AI Agent. Your goal is to represent Sameer by answering questions about his expertise, resume, and projects using this context: {PROFILE_CONTEXT}. You are also a world-class engineer, so you can answer general technical questions, but always try to relate them back to Sameer's skills when relevant. Be professional, concise, and helpful."
)

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="Gemini API Key not configured on server.")

    try:
        # Initialize chat with history
        chat = model.start_chat(history=[
            {"role": "user" if m.role == "user" else "model", "parts": [{"text": m.content}]}
            for m in request.history
        ])

        response = chat.send_message(request.message)
        
        # Accessing .text can fail if the model blocked the response (Safety Filters)
        try:
            reply_text = response.text
        except (ValueError, AttributeError):
            reply_text = "I'm sorry, I can't provide an answer to that right now. Please try asking something else about my experience."
            
        return {"reply": reply_text}
    except Exception as e:
        # Log the actual error to your terminal for debugging
        print(f"AI Assistant Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal AI Processing Error")

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