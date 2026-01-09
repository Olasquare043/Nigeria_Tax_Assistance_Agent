from fastapi import FastAPI, HTTPException, status, Request  
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime
import uvicorn
import os
import sys
import uuid
from pathlib import Path

# Import routers
from chat import router as chat_router
from ingest import router as ingest_router
from auth import router as auth_router

# Import error handlers
from errors import (
    AppException, AuthenticationError, AuthorizationError,
    ValidationException, NotFoundError, RateLimitError, ServiceError,
    ErrorResponse, create_error_response
)

# Check AI Engine Availability 
CURRENT_DIR = Path(__file__).resolve().parent  # backend/
PROJECT_ROOT = CURRENT_DIR.parent  # project_root/
AI_ENGINE_PATH = PROJECT_ROOT / "ai_engine"

print(f" Starting Taxify AI assistant")
print(f" Project root: {PROJECT_ROOT}")
print(f" AI Engine path: {AI_ENGINE_PATH}")

if AI_ENGINE_PATH.exists():
    print(f" AI Engine folder found")
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
else:
    print(f" WARNING: AI Engine folder not found at {AI_ENGINE_PATH}")
    print(f" The /chat and /ingest endpoints will not work!")

load_dotenv()

app = FastAPI(
    title="Taxify AI Assistant",
    version="1.0.0",
    description="Agentic RAG System for Nigerian Tax Reform Bills",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def handle_app_exception(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    error_response = ErrorResponse(
        error=exc.error_code,
        message=exc.message,
        detail=exc.detail,
        code=exc.code,
        timestamp=datetime.now().isoformat(),
        request_id=str(request.state.request_id) if hasattr(request.state, 'request_id') else None
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    error_response = ErrorResponse(
        error="HTTP_ERROR",
        message=exc.detail,
        detail=None,
        code=f"HTTP-{exc.status_code}",
        timestamp=datetime.now().isoformat()
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(Exception)
async def handle_generic_exception(request: Request, exc: Exception):
    """Handle all other exceptions"""
    import traceback
    error_details = traceback.format_exc()
    
    # Log the error (in production, use proper logging)
    print(f"Unhandled exception: {exc}")
    print(f"Traceback: {error_details}")
    
    error_response = ErrorResponse(
        error="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        detail="Our team has been notified. Please try again later.",
        code="SRV-5001",
        timestamp=datetime.now().isoformat(),
        request_id=str(uuid.uuid4())
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )

# Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests"""
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    duration = (datetime.now() - start_time).total_seconds() * 1000
    
    
    print(f"{request.method} {request.url.path} - {response.status_code} - {duration:.2f}ms")
    
    return response

# routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])

# Health and info endpoints
@app.get("/")
def home():
    return {
        "service": "Taxify AI Assistant",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "features": {
            "authentication": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "profile": "GET /api/auth/me",
                "password_reset": "POST /api/auth/forgot-password",
                "change_password": "PUT /api/auth/change-password"
            },
            "chat": {
                "new_chat": "POST /api/chat",
                "history": "GET /api/history/{session_id}",
                "my_conversations": "GET /api/my-conversations"
            },
            "admin": {
                "ingest_documents": "POST /api/ingest",
                "ingest_status": "GET /api/ingest/status"
            }
        },
        "security": {
            "rate_limiting": "Enabled",
            "authentication": "JWT Bearer tokens",
            "password_hashing": "bcrypt"
        },
        "ai_engine": "Agentic RAG with LangGraph",
        "database": "MySQL with conversation history"
    }

@app.get("/health")
def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "tax-reform-api",
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    try:
        # Check database
        from database import db_manager
        with db_manager.engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check AI engine
    try:
        from chat import AI_ENGINE_AVAILABLE
        health_status["components"]["ai_engine"] = "available" if AI_ENGINE_AVAILABLE else "unavailable"
        if not AI_ENGINE_AVAILABLE:
            health_status["status"] = "degraded"
    except:
        health_status["components"]["ai_engine"] = "unknown"
    
    return health_status

@app.get("/metrics")
async def get_metrics():
    """Basic metrics endpoint"""
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "uptime": "todo",
            "requests_served": "todo",
            "active_users": "todo"
        }
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
        log_level="info",
        access_log=True
    )