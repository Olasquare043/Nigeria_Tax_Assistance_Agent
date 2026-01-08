from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import hashlib
import json
import sys
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

# Database
from database import get_db

router = APIRouter()

#  AI engine import path
CURRENT_DIR = Path(__file__).resolve().parent  # backend/
PROJECT_ROOT = CURRENT_DIR.parent  # project_root/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import AI engine components 
try:
    from ai_engine.tax_engine.ingest import ingest_pdfs
    from ai_engine.tax_engine.vectorstore import upsert_incremental
    from ai_engine.tax_engine.config import settings
    AI_INGEST_AVAILABLE = True
    print("AI Engine ingest module loaded")
except ImportError as e:
    AI_INGEST_AVAILABLE = False
    print(f" AI Engine ingest import failed: {e}")
    print(f" Python path: {sys.path}")
    print(f" Project root: {PROJECT_ROOT}")

# Pydantic models
class IngestResponse(BaseModel):
    success: bool
    message: str
    stats: dict
    timestamp: str
    documents_processed: int

class IngestRequest(BaseModel):
    force_rebuild: bool = False
    chunk_size: int = 3500
    overlap: int = 300

def sha1_text(text: str) -> str:
    """Generate SHA1 hash for content deduplication"""
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    request: IngestRequest = None,
    db: Session = Depends(get_db)
):
    """
    Rebuild the vector database from PDF documents.
    """
    if not AI_INGEST_AVAILABLE:
        raise HTTPException(
            status_code=500, 
            detail="AI Engine not available. Check that ai_engine folder exists at project root."
        )
    
    if request is None:
        request = IngestionRequest()
    
    try:
        print("📂 Starting document ingestion...")
        start_time = datetime.now()
        
        # Ingest PDFs - functions already imported
        docs = ingest_pdfs()
        
        if not docs:
            raise HTTPException(
                status_code=400,
                detail="No documents found in docs/ folder. Add PDF files first."
            )
        
        print(f" Extracted {len(docs)} document chunks")
        
        # content hash for deduplication
        for doc in docs:
            if "content_hash" not in doc.metadata:
                doc.metadata["content_hash"] = sha1_text(doc.page_content)
        
        # Update vector database
        stats = upsert_incremental(docs)
        
        # Log to database
        try:
            db.execute(
                text("""
                    INSERT INTO system_logs (action, details, timestamp)
                    VALUES ('ingest', :details, NOW())
                """),
                {
                    "details": json.dumps({
                        "chunks_processed": len(docs),
                        "stats": stats,
                        "request": request.dict(),
                        "duration_seconds": (datetime.now() - start_time).total_seconds()
                    })
                }
            )
            db.commit()
        except Exception as log_error:
            print(f" Failed to log to database: {log_error}")
        
        # Prepare response
        duration = (datetime.now() - start_time).total_seconds()
        
        return IngestResponse(
            success=True,
            message=f"Ingestion completed in {duration:.1f}s",
            stats=stats,
            timestamp=datetime.now().isoformat(),
            documents_processed=len(docs)
        )
        
    except FileNotFoundError as e:
        error_msg = f"PDF files not found: {str(e)}"
        print(f" {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    except HTTPException:
        raise
    
    except Exception as e:
        error_msg = f"Ingestion failed: {str(e)}"
        print(f" {error_msg}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail=error_msg
        )

@router.get("/ingest/status")
async def get_ingest_status(db: Session = Depends(get_db)):
    """Get latest ingestion status"""
    try:
        result = db.execute(
            text("""
                SELECT details, timestamp 
                FROM system_logs 
                WHERE action = 'ingest' 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
        ).fetchone()
        
        if result:
            details = json.loads(result[0]) if result[0] else {}
            return {
                "last_ingest": result[1].isoformat() if result[1] else None,
                "details": details,
                "status": "has_history"
            }
        else:
            return {
                "status": "never_run",
                "message": "Ingestion has never been run via API"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }