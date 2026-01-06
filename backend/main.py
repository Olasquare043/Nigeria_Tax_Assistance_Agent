from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware 
from dotenv import load_dotenv
from datetime import datetime
import uvicorn
import os
import sys
from pathlib import Path

# ===== Check AI Engine Availability =====
CURRENT_DIR = Path(__file__).resolve().parent  # backend/
PROJECT_ROOT = CURRENT_DIR.parent  # project_root/
AI_ENGINE_PATH = PROJECT_ROOT / "ai_engine"

print(f"🚀 Starting Nigeria Tax Reform Assistant")
print(f"📁 Project root: {PROJECT_ROOT}")
print(f"📁 AI Engine path: {AI_ENGINE_PATH}")

if AI_ENGINE_PATH.exists():
    print(f"✅ AI Engine folder found")
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
else:
    print(f"⚠️ WARNING: AI Engine folder not found at {AI_ENGINE_PATH}")
    print(f"⚠️ The /chat and /ingest endpoints will not work!")

# Import routers
from chat import router as chat_router
from ingest import router as ingest_router

load_dotenv()
app = FastAPI(
    title="Nigeria Tax Reform 2024 Q&A Assistant",
    version="1.0.0",
    description="Agentic RAG System for Nigerian Tax Reform Bills"
)


# CORS Configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173"],  # Added for eval
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")  # NEW

@app.get("/")
def home():
    return {
        "message": "Nigeria Tax Reform Bills 2024 Q&A Assistant",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "history": "/api/history/{session_id}",
            "ingest": "/api/ingest",  # NEW
            "new_session": "/api/new-session",
            "health": "/health"
        },
        "ai_engine": "Agentic RAG with LangGraph",
        "database": "MySQL for conversation history"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "tax-reform-api",
        "ai_engine": "integrated"
    }

# For evaluation compatibility
@app.get("/health-check")
def health_check_alternative():
    """Alternative health check for evaluation system"""
    return {"ok": True}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=port,
        log_level="info"
    )